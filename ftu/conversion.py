from pathlib import Path

import pandas as pd
import numpy as np
import netCDF4 as nc
import logging

from ftu.grid import Grid

logger = logging.getLogger(__name__)

from groundmodel.core import SoilColumn, Layer, Material, Property
from groundmodel.operations import use_defaults_if_missing
from ftu.FreThaw1D_gridcreator import (write_grid_netCDF, 
                                    grid1D, 
                                    set_initial_excess_ice,
                                    set_regrid_parameters,
                                    extract_grid_for_shallow_spinup,
                                    set_initial_condition,
                                    set_parameters)

SampleLayer1 = Layer({
           'p::layer_thickness': 1.0,
           'freethaw::par1': 0.65, 
           'freethaw::par2': 1.67,
           'freethaw::par3': np.nan,
           'freethaw::par4': np.nan,
           'freethaw::meltingTemperature': 273.15,
           'freethaw::thetaR': 0.49,
           'freethaw::thetaS': 0.01,
           'freethaw::specificThermalCapacity': 699,
           'freethaw::thermalConductivity': 3.2,
           'freethaw::density': 2755.0,
           'freethaw::ic': 270.0,
           'freethaw::EI_ratio': 0.1,
           'freethaw::volumeExcessIce': 5.0,
           'freethaw::equationStateID': 0})

SampleLayer2 = SampleLayer1.union(Layer({'p::layer_thickness': 2.0,
                                         'freethaw::density': 2000.0,
                                         'freethaw::EI_ratio': 0.0,
                                         'freethaw::ic': 271.0,}))

SampleColumn =  SoilColumn([SampleLayer1, 
                            SampleLayer2])


def get_lower_boundaries(column: SoilColumn) -> np.ndarray:
    "Get the eta values for a SoilColumn object."
    
    dz = column.layer_thicknesses  # TODO: ensure this is using the right one
    eta = -np.cumsum(dz)
    
    return eta

def get_layer_midpoints(column: SoilColumn) -> np.ndarray:
    "Get the midpoints of each layer in a SoilColumn object."
     
    dz = column.layer_thicknesses
    eta = -np.cumsum(dz)
    midpoints = eta + dz / 2
    
    return midpoints

# scipy interp1d `kind` that the grid creator must use for each interpolation mode
INTERPOLATION_KINDS = {"step": "next", "linear": "linear"}


def layer_profile(column: SoilColumn, values: np.ndarray, interpolation: str) -> tuple[np.ndarray, np.ndarray]:
    """Build the (eta, value) points used to interpolate a per-layer property onto the grid.

    'step':   a point at the top of each layer (plus the column bottom). With interp1d(kind='next')
              each cell takes the value of the nearest point above it, so the value changes
              exactly at layer boundaries.
    'linear': a point at each layer midpoint (plus the surface and column bottom), so the value
              varies linearly between layer midpoints.
    """
    lb = get_lower_boundaries(column)

    if interpolation == "step":
        eta = np.concat([np.array([0]), lb])
        values = np.concat([values, values[-1:]])
    elif interpolation == "linear":
        eta = np.concat([np.array([0]), get_layer_midpoints(column), lb[-1:]])
        values = np.concat([values[:1], values, values[-1:]])
    else:
        raise ValueError(f"interpolation must be one of {list(INTERPOLATION_KINDS)}, got {interpolation}")

    return eta, values


def column_to_ic_csv(column: SoilColumn, interpolation: str = "linear") -> pd.DataFrame:
    "Convert a SoilColumn object to a DataFrame containing the initial condition (ic) for each layer."
    eta, ic = layer_profile(column, column.extract('freethaw::ic'), interpolation)

    return pd.DataFrame({'eta': eta, 'T0': ic})


def column_to_ratio_csv(column: SoilColumn, interpolation: str = "step") -> pd.DataFrame:
    if "freethaw::EI_ratio" in column.property_names:
        r = column.extract('freethaw::EI_ratio')
    elif "freethaw::volumeExcessIce" in column.property_names and "freethaw::volumeSoil" in column.property_names:
        eiv = column.extract('freethaw::volumeExcessIce')
        sv = column.extract('freethaw::volumeSoil')
        r = 1 / (1 + sv / eiv)
    else:
        raise ValueError("Column does not contain the necessary properties for calculating the ice-to-soil ratio.")

    # Layers without excess ice properties have no excess ice (a NaN here becomes a NaN soil volume in the grid)
    r = np.nan_to_num(r, nan=0.0)

    eta, r = layer_profile(column, r, interpolation)

    return pd.DataFrame({'eta': eta, 'EI_ratio': r})


def column_to_parameter_csv(column: SoilColumn, drop_duplicates=True) -> pd.DataFrame:
    df = column.as_dataframe()
    df = df.rename(columns=lambda c: c.replace("freethaw::", ""))
    df = df.rename(columns=lambda c: c.replace("meltingTemperature", "meltingT"))
    df = df.rename(columns=lambda c: c.replace("specificThermalCapacity", "specificHeatCapacity"))

    raw =  df.loc[:, ["density",
                      "thermalConductivity",
                      "specificHeatCapacity",
                      "thetaS",
                      "thetaR",
                      "meltingT",
                      "par1",
                      "par2",
                      "par3",
                      "par4"]]

    if drop_duplicates:
        return raw.drop_duplicates().reset_index(drop=True)

    return raw

def column_to_grid_csv(column: SoilColumn) -> pd.DataFrame:
    """Convert a SoilColumn object to a DataFrame containing the grid data.
    Type,eta,K,equationStateID,parameterID
       L,0,nan,0,0
       L,-100,nan,1,1
       L,-200,nan,nan,nan
    """
    eta = get_lower_boundaries(column)
    eta = np.concat([np.array([0]), eta])  
    
    eqnstate = column.extract('freethaw::equationStateID')
    eqnstate = np.concat([eqnstate.astype('str'), np.array(["nan"])]) 

    material = column_to_parameter_csv(column, drop_duplicates=False)
    material["paramID"] = pd.factorize(material.apply(tuple, axis=1))[0]  # group unique parameterIDs
    material['layerNumber'] = np.arange(len(material)).astype('str')

    parameterid = material["paramID"].copy()
    parameterid = pd.concat([parameterid, pd.Series([pd.NA])], ignore_index=True)
    
    return pd.DataFrame({"Type": "L",
                         'eta': eta,
                         'K': "nan",
                         'equationStateID': eqnstate,
                         'parameterID': parameterid})


def column_to_grids(soilcolumn: SoilColumn,
                    create_files_in:str,
                    regrid_input_file_name:str,
                    name='newGrid',
                    shallow_grid_depth:float=10,
                    dz_min:float=0.01,
                    b:float=0.01,
                    grid_type:str='exponential',
                    defaults_if_missing=True,
                    ic_interpolation:str='linear',
                    ei_interpolation:str='step'):
    """ic_interpolation / ei_interpolation: 'step' keeps each layer's value constant with jumps at
    layer boundaries; 'linear' interpolates between layer midpoints."""
    if defaults_if_missing:
        use_defaults_if_missing(soilcolumn, ['freethaw::par3', 'freethaw::par4'])

    if not grid_type in ['exponential', 'classical']:
        raise ValueError(f"grid_type must be either 'exponential' or 'classical', got {grid_type}")

    for interpolation in (ic_interpolation, ei_interpolation):
        if interpolation not in INTERPOLATION_KINDS:
            raise ValueError(f"interpolation must be one of {list(INTERPOLATION_KINDS)}, got {interpolation}")

    logger.info(f"Creating Grid: {name} in {create_files_in}")
    grid_input_file_name = str(Path(create_files_in) / f"{name}_grid.csv")
    parameter_input_file_name = str(Path(create_files_in) / f"{name}_parameter.csv")
    ei_input_file_name = str(Path(create_files_in) / f"{name}_ei.csv")
    ic_input_file_name = str(Path(create_files_in) / f"{name}_ic.csv")
    output_file_name =  str(Path(create_files_in) / "deepGrid.nc")
    output_file_name_shallow_grid = str(Path(create_files_in) / "shallowGrid.nc")

    output_title ="" 
    output_title_shallow_grid = "" 
    output_summary = "" 
    output_summary_shallow_grid ="" 
    output_date = "" 
    output_institution = ''

    size_factor = 5

    interp_model_ic = INTERPOLATION_KINDS[ic_interpolation]
    interp_model_EI_ratio = INTERPOLATION_KINDS[ei_interpolation]

    data_grid = column_to_grid_csv(soilcolumn)
    data_ic = column_to_ic_csv(soilcolumn, ic_interpolation)
    data_EI_ratio = column_to_ratio_csv(soilcolumn, ei_interpolation)
    data_parameter = column_to_parameter_csv(soilcolumn, drop_duplicates=True)

    data_grid.to_csv(grid_input_file_name, index=False)
    data_ic.to_csv(ic_input_file_name, index=False)
    data_EI_ratio.to_csv(ei_input_file_name, index=False)
    data_parameter.to_csv(parameter_input_file_name, index=False)
   
    data_regrid = pd.read_csv(regrid_input_file_name)
   # print(data_parameter)
    #print(data_grid)
    #import pdb;pdb.set_trace()
    [KMAX, VECTOR_LENGTH, eta, eta_dual, space_delta, z, z_dual, control_volume] = grid1D(data_grid, dz_min, b, grid_type, size_factor=size_factor)
    logger.info(f"KMAX={KMAX}, VEC_LEN={VECTOR_LENGTH}")

    ic = set_initial_condition(data_ic, eta, interp_model_ic,fill_value=0.0)

    [excess_ice_volume,soil_volume] = set_initial_excess_ice(data_EI_ratio, eta, ic, control_volume, interp_model_EI_ratio,fill_value=0.0)

    [regrid_ID, buffer_temperature_close_to_zero_isotherm, control_volume_size_close_to_zero_isotherm] = set_regrid_parameters(data_regrid, eta)

    [equation_state_ID, parameter_ID, density, thermal_conductivity, specific_heat_capacity, theta_s, theta_r,
    melting_temperature, par_1, par_2, par_3, par_4] = set_parameters(data_grid, data_parameter, KMAX, VECTOR_LENGTH, eta)

    [idk, shallow_grid_eta, shallow_grid_eta_dual, shallow_grid_z, shallow_grid_z_dual, shallow_grid_space_delta, shallow_grid_soil_volume, 
    shallow_grid_excess_ice_volume, shallow_grid_ic, shallow_grid_equation_state_ID, shallow_grid_parameter_ID, 
    shallow_grid_regrid_ID, shallow_grid_KMAX] = extract_grid_for_shallow_spinup(shallow_grid_depth, eta, eta_dual, z, z_dual, space_delta, soil_volume, ic, excess_ice_volume, equation_state_ID, parameter_ID, regrid_ID, KMAX, 
                        VECTOR_LENGTH)

    # Shallow
    write_grid_netCDF(shallow_grid_eta, shallow_grid_eta_dual, shallow_grid_z, 
                    shallow_grid_z_dual, shallow_grid_space_delta, 
                    shallow_grid_soil_volume, shallow_grid_ic, 
                    shallow_grid_excess_ice_volume, 
                    shallow_grid_equation_state_ID, shallow_grid_parameter_ID,
                    shallow_grid_regrid_ID, shallow_grid_KMAX, VECTOR_LENGTH,
                    buffer_temperature_close_to_zero_isotherm,
                    control_volume_size_close_to_zero_isotherm, density,
                    thermal_conductivity, specific_heat_capacity, theta_s,
                    theta_r, melting_temperature, par_1, par_2, par_3, par_4,
                    output_file_name_shallow_grid, output_title_shallow_grid,
                    output_institution, output_summary_shallow_grid,
                    output_date, grid_input_file_name,
                    parameter_input_file_name)

    # Deep
    write_grid_netCDF(eta, eta_dual, z, z_dual, space_delta, soil_volume, ic,
                    excess_ice_volume, equation_state_ID, parameter_ID,
                    regrid_ID, KMAX, VECTOR_LENGTH,
                    buffer_temperature_close_to_zero_isotherm,
                    control_volume_size_close_to_zero_isotherm,
                    density, thermal_conductivity, specific_heat_capacity,
                    theta_s, theta_r, melting_temperature, par_1, par_2,
                    par_3, par_4, output_file_name, output_title,
                    output_institution, output_summary, output_date,
                    grid_input_file_name, parameter_input_file_name)


def nc_grid_to_column(nc_file_path: str) -> SoilColumn:
    g = Grid(nc_file_path)
    with nc.Dataset(nc_file_path, 'r') as ds:
        materials = _materials_from_dataset(ds)
    thicknesses = g.layer_thicknesses()  # Bottom to top, same order as the depth variables
    layers = []
    
    for i, dz in enumerate(thicknesses):
        layerdata = {}
        
        layerdata['freethaw::__layer_thickness'] = dz
        
        for dname in g.depth_names():
            if dname in ['eta', 'z']:
                continue  # Skip these depth variables. We only care about thickness
            layerdata[f"freethaw::{dname}"] = g[dname][i]

        layerdata["PARAMETERID"] = g['parameterID'][i]
        # Per-cell ratio, so that only cells with the same excess ice ratio are merged below
        layerdata["freethaw::EI_ratio"] = g['volumeExcessIce'][i] / (g['volumeExcessIce'][i] + g['volumeSoil'][i])
        layers.append(Layer(layerdata, metadata={"role_bindings": {"layer_thickness": "freethaw::__layer_thickness"}}))

    col = SoilColumn(layers[::-1])  # Reverse to get top to bottom
    merged_col = col.merge_identical_layers(sum_props=['freethaw::volumeExcessIce',
                                                       'freethaw::volumeSoil',
                                                       'freethaw::__layer_thickness'])

    for layer in merged_col.layers:
        i = int(layer['PARAMETERID'].value)
        for prop in materials[i].properties.values():
            layer.add_property(prop)

    return merged_col


def _materials_from_dataset(dataset: nc.Dataset) -> list[Material]:
    materials = []
    for i in range(len(dataset.dimensions['parameter'])):
        material = _make_material(dataset, i)
        materials.append(material)
    return materials
 

def _make_material(dataset: nc.Dataset, index: int) -> Material:
    material_data = {}
    for var in dataset.variables:
        if len(dataset[var].dimensions) == 1 and dataset[var].dimensions[0] == 'parameter':  # 
            prop_value = dataset.variables[var][index]
            prop_name = f"freethaw::{var}"
            prop_units = dataset.variables[var].units if 'units' in dataset.variables[var].ncattrs() else ""
            material_data[prop_name] = Property(name=prop_name, value=prop_value, units=prop_units)
            
    return Material(data=material_data)


if __name__ == "__main__":
    nc_file_path = r"C:\Users\nicho\Downloads\deepGrid.nc"
    nc_grid_to_column(nc_file_path)
    column = SampleColumn
    print(column_to_ic_csv(column))
    print(column_to_ratio_csv(column))
    print(column_to_parameter_csv(column))
    print(column_to_grid_csv(column))
    column_to_grids(column,
                    create_files_in=r"C:/Users/nicho/downloads",
                    regrid_input_file_name=r"C:\Users\nicho\src\FreeThawUtil\ftu\data\grid_input\regrid.csv",
                    name='newGrid',
                    shallow_grid_depth=10,
                    dz_min=0.01,
                    b=0.01,
                    grid_type='exponential')