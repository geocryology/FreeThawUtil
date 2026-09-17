from groundmodel.core import SoilColumn, Layer
import pandas as pd
import numpy as np

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

def column_to_ic(column: SoilColumn) -> pd.DataFrame:
    "Convert a SoilColumn object to a DataFrame containing the initial condition (ic) for each layer."
    lb = get_lower_boundaries(column)
    midpoints = get_layer_midpoints(column)
    eta = np.concat([np.array([0]), midpoints, lb[-1:]]) 
    
    ic = column.extract('freethaw::ic')
    ic = np.concat([ic[:1], ic, ic[-1:]])  
    
    return pd.DataFrame({'eta': eta, 'T0': ic})


def column_to_ratio(column: SoilColumn) -> pd.DataFrame:
    lb = get_lower_boundaries(column)
    midpoints = get_layer_midpoints(column)
    eta = np.concat([np.array([0]), midpoints, lb[-1:]])  
    
    if "freethaw::volumeExcessIce" in column.property_names and "freethaw::volumeSoil" in column.property_names:
        eiv = column.extract('freethaw::volumeExcessIce')
        sv = column.extract('freethaw::volumeSoil')
        r = 1 / (1 + sv / eiv)
    elif "freethaw::EI_ratio" in column.property_names:
        r = column.extract('freethaw::EI_ratio') * np.nan
    else:
        raise ValueError("Column does not contain the necessary properties for calculating the ice-to-soil ratio.")

    r = np.concat([r[:1], r, r[-1:]])  
    
    return pd.DataFrame({'eta': eta, 'EI_ratio': r})


def column_to_parameter(column: SoilColumn) -> pd.DataFrame:
    df = column.as_dataframe()
    df = df.rename(columns=lambda c: c.replace("freethaw::", ""))
    df = df.rename(columns=lambda c: c.replace("meltingTemperature", "meltingT"))
    df = df.rename(columns=lambda c: c.replace("specificThermalCapacity", "specificHeatCapacity"))
    
    return df.loc[:, ["density",
                      "thermalConductivity",
                      "specificHeatCapacity",
                      "thetaS",
                      "thetaR",
                      "meltingT",
                      "par1",
                      "par2",
                      "par3",
                      "par4"]]

def column_to_grid(column: SoilColumn) -> pd.DataFrame:
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
    
    parameterid = np.arange(len(eta)).astype('str')
    parameterid[-1] = "nan"
    
    return pd.DataFrame({"Type": "L",
                         'eta': eta,
                         'K': "nan",
                         'equationStateID': eqnstate,
                         'parameterID': parameterid})



if __name__ == "__main__":
    column = SampleColumn
    print(column_to_ic(column))
    print(column_to_ratio(column))
    print(column_to_parameter(column))
    print(column_to_grid(column))