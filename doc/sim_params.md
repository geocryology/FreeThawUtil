In the simfile, variables can be defined:

```
def tcwater = 3
```

These can be used to define other variables, which may be identical for different components of the model:

```
* solver.thermalConductivityWater" = ${param2}
* solver_spin_up_in_depth.thermalConductivityWater" = ${param2}
```

* home home the path of the project folder. It is used to define the local path for input and output files.




## solver
* "solver.waterDensity" [waterDensity](#physical-parameters)
* "solver.iceDensity" ice density [waterDensity](#physical-parameters)
* "solver.specificThermalCapacityWater" [specificThermalCapacityWater](#physical-parameters)
* "solver.specificThermalCapacityIce" [specificThermalCapacityIce](#physical-parameters)
* "solver.thermalConductivityWater"  [thermalConductivityWater](#physical-parameters)
* "solver.thermalConductivityIce" [thermalConductivityIce](#physical-parameters)
* "solver.latentHeatFusion" [latentHeatFusion](#physical-parameters)
* "solver.referenceTemperatureInternalEnergy"  [referenceTemperatureInternalEnergy](#physical-parameters)

* "solver.sfccModel" [sfccModel](#physical-models)
* "solver.equationStateModel" [equationStateModel](#physical-models)
* "solver.soilThermalConductivityModel"  [soilThermalConductivityModel](#physical-models)
* "solver.thermalConductivityModel"     [thermalConductivityModel](#physical-models)
* "solver.interfaceConductivityModel"   [interfaceThermalConductivityModel](#physical-models)

* "solver.topBCType" [topBCType](#boundary-conditions)
* "solver.bottomBCType"  [bottomBCType](#boundary-conditions)

* "solver.aMin" [aMin](#physical-parameters)
* "solver.aMax" [aMax](#physical-parameters)
* "solver.bMin" [bMin](#physical-parameters)
* "solver.bMax" [bMax](#physical-parameters)

* "solver.newtonTolerance" nested Newton tolerance | "0.033370"
* "solver.nestedNewton" Algorithm to solve the nonlinear system: 0 (Newton's method), 1(nested Newton (suggested))
* "solver.tTimestep" [tTimestep](#time) time step [s], it must be consistent with tTimestep
* "solver.timeDelta" time step [s] used to integrate the equation, * this is the Delta t used in the numerical scheme  timeDelta <= tTimestep
* "solver.picardIteration" Number of Picard iteration during each time step to update the values of thermal conductivity with the new solution

### Solver spin-up in depth
* "solver_spin_up_in_depth.waterDensity" [waterDensity](#physical-parameters)
* "solver_spin_up_in_depth.iceDensity" [iceDensity](#physical-parameters)
* "solver_spin_up_in_depth.specificThermalCapacityWater" [specificThermalCapacityWater](#physical-parameters)
* "solver_spin_up_in_depth.specificThermalCapacityIce" [specificThermalCapacityIce](#physical-parameters)
* "solver_spin_up_in_depth.thermalConductivityWater" [thermalConductivityWater](#physical-parameters)
* "solver_spin_up_in_depth.thermalConductivityIce" [thermalConductivityIce](#physical-parameters)
* "solver_spin_up_in_depth.latentHeatFusion" [latentHeatFusion](#physical-parameters)
* "solver_spin_up_in_depth.referenceTemperatureInternalEnergy" [referenceTemperatureInternalEnergy](#physical-parameters)

* "solver_spin_up_in_depth.sfccModel" [sfccModel](#physical-models)
* "solver_spin_up_in_depth.soilThermalConductivityModel" [soilThermalConductivityModel](#physical-models)
* "solver_spin_up_in_depth.thermalConductivityModel"  [thermalConductivityModel](#physical-models)
* "solver_spin_up_in_depth.interfaceConductivityModel"  [interfaceThermalConductivityModel](#physical-models)

* "solver_spin_up_in_depth.aMin" [aMin](#physical-parameters)
* "solver_spin_up_in_depth.aMax" [aMax](#physical-parameters)
* "solver_spin_up_in_depth.bMin" [bMin](#physical-parameters)
* "solver_spin_up_in_depth.bMax" [bMax](#physical-parameters)

* "solver_spin_up_in_depth.geothermalFlux" [geothermalFlux](#physical-parameters)

## Readers

* "reader_NetCDF_shallow_grid.gridFilename" File path of grid.nc file, the file created with 1_excess_ice_grid.ipynb "${pathGridShallow}"

### top boundary condition
// parameters of the reader for input top boundary condition values
* reader_data_topBC.file" (_str_) Path to the file containing the top boundary condition values
* reader_data_topBC.idfield"          [idfield](#input-and-output-files) 
* "reader_data_topBC.tStart" [tstart](#time)
* reader_data_topBC.tEnd"             [tEnd](#time)
* reader_data_topBC.tTimestep"        [tTimestep](#time)
* reader_data_topBC.fileNovalue"      "-9999"

### bottom boundary condition
// parametersof the reader for bottom boundary condition values
* reader_data_bottomBC.file" (_str_) Path to the file containing the bottom boundary condition values
* reader_data_bottomBC.idfield"          [idfield](#input-and-output-files) 
* "reader_data_bottomBC.tStart"           [tstart](#time)
* reader_data_bottomBC.tEnd"             [tEnd](#time)
* reader_data_bottomBC.tTimestep"        [tTimestep](#time)
* reader_data_bottomBC.fileNovalue"      "-9999"

### save dates
// parameters of the reader for date saving
* reader_data_inSaveDates.file" (_str_) Path to the file containing the date saving values
* reader_data_inSaveDates.idfield"          [idfield](#input-and-output-files) 
* reader_data_inSaveDates.tStart"           [tstart](#time)
* reader_data_inSaveDates.tEnd"             [tEnd](#time)
* reader_data_inSaveDates.tTimestep"        [tTimestep](#time)
* reader_data_inSaveDates.fileNovalue"      "-9999"

### heat transfer coefficient
// parameters of the reader for heat transfer coefficient
* reader_data_inHeatTransferCoefficient.file"  (_str_) Path to the file containing the heat transfer coefficient values
* reader_data_inHeatTransferCoefficient.idfield"          [idfield](#input-and-output-files) 
* reader_data_inHeatTransferCoefficient.tStart"           [tstart](#time)
* reader_data_inHeatTransferCoefficient.tEnd"             [tEnd](#time)
* reader_data_inHeatTransferCoefficient.tTimestep"        [tTimestep](#time)
* reader_data_inHeatTransferCoefficient.fileNovalue"      "-9999"

### snow cover
* reader_data_inSnowCover.file" (_str_) Path to the file containing the snow cover timeseries (0 = no snow, 1 = snow cover)
* reader_data_inSnowCover.idfield"          "ID"
* reader_data_inSnowCover.tStart"           [tstart](#time)
* reader_data_inSnowCover.tEnd"             [tEnd](#time)
* reader_data_inSnowCover.tTimestep"        [tTimestep](#time)
* reader_data_inSnowCover.fileNovalue"      "-9999"

### short wave net
* reader_data_inShortWaveNet.file"  (_str_) Path to the file containing the short wave net values
* reader_data_inShortWaveNet.idfield"          [idfield](#input-and-output-files) 
* reader_data_inShortWaveNet.tStart"           [tstart](#time)
* reader_data_inShortWaveNet.tEnd"             [tEnd](#time)
* reader_data_inShortWaveNet.tTimestep"        [tTimestep](#time)
* reader_data_inShortWaveNet.fileNovalue"      "-9999"


## Writers
			
### writer spinup
* writer_NetCDF_shallow_spinup.fileName" (_str_) Path to the file containing the "${pathShallowSpinupMeanT}"
* writer_NetCDF_shallow_spinup.writeFrequency" "${writingFrequency}"

* writer_NetCDF_shallow_spinup.briefDescritpion" " "
* writer_NetCDF_shallow_spinup.topBC" "${topBCType}"
* writer_NetCDF_shallow_spinup.bottomBC" "${bottomBCType}"
* writer_NetCDF_shallow_spinup.pathTopBC" "${pathTopBC}"
* writer_NetCDF_shallow_spinup.pathBottomBC" "${pathBottomBC}"
* writer_NetCDF_shallow_spinup.pathGrid" "${pathGridShallow}"
* writer_NetCDF_shallow_spinup.timeDelta" "86400s"
* writer_NetCDF_shallow_spinup.sfccModel" "${sfccModel}"
* writer_NetCDF_shallow_spinup.equationStateModel" "${equationStateModel}"
* writer_NetCDF_shallow_spinup.soilThermalConductivityModel" "${soilThermalConductivityModel}"
* writer_NetCDF_shallow_spinup.thermalConductivityModel" "${thermalConductivityModel}"
* writer_NetCDF_shallow_spinup.interfaceThermalConductivityModel" "${interfaceThermalConductivityModel}"
* writer_NetCDF_shallow_spinup.timeUnits" "Minutes since 01/01/1970 00:00:00 UTC"

### writer backup
* writer_NetCDF_backup.fileName" "${pathOutputShallowSpinupBackUp}"
* writer_NetCDF_backup.writeFrequency" "${writingFrequency}"

* writer_NetCDF_backup.briefDescritpion" " "
* writer_NetCDF_backup.topBC" "${topBCType}"
* writer_NetCDF_backup.bottomBC" "${bottomBCType}"
* writer_NetCDF_backup.pathTopBC" "${pathTopBC}"
* writer_NetCDF_backup.pathBottomBC" "${pathBottomBC}"
* writer_NetCDF_backup.pathGrid" "${pathGridShallow}"
* writer_NetCDF_backup.timeDelta" "86400s"
* writer_NetCDF_backup.sfccModel" "${sfccModel}"
* writer_NetCDF_backup.equationStateModel" "${equationStateModel}"
* writer_NetCDF_backup.soilThermalConductivityModel" "${soilThermalConductivityModel}"
* writer_NetCDF_backup.thermalConductivityModel" "${thermalConductivityModel}"
* writer_NetCDF_backup.interfaceThermalConductivityModel" "${interfaceThermalConductivityModel}"
* writer_NetCDF_backup.timeUnits" "Minutes since 01/01/1970 00:00:00 UTC"


### Buffer
* buffer_spinup.writeFrequency" "${writingFrequency}"
* buffer_spinup.referenceKMAX" "${spinupGridInterpolationKMAX}"

* buffer_backup.writeFrequency" "${writingFrequency}"

### ???

* reader_NetCDF_deep_grid.gridFilename" 					"${pathGridDeep}"
* reader_NetCDF_shallow_grid_backup.gridFilename"  		"${pathShallowSpinupBackUp}"
* reader_NetCDF_spin_up_mean_T.gridFilename" 		 	"${pathShallowSpinupMeanT}"
* writer_NetCDF_spinup_in_depth.gridFileName"	  "${pathOutputSpinUpInDepth}"
* writer_NetCDF_spinup_in_depth.briefDescritpion"  ""



# Shared parameters

## Time
* tStart (_str, YYYY-MM-DD HH:MM_) | "2000-01-01 00:00"
* tEnd  (_str, YYYY-MM-DD HH:MM_)  | "2020-01-01 00:00"
* tTimestep (_int_) time interval of temporal series [minutes] | 1440
* writingFrequency (_int_) | 1000


## physical parameters

* aMin (_real_) | 0.0180
* bMin (_real_) | 0.0090
* aMax (_real_) | 0.0210
* bMax (_real_) | 0.0110
* geothermalFlux (_real_) [W /m2] | 0.0500
* spinupGridInterpolationKMAX () | 20000

* waterDensity (_real_) density of water [kg/m3] | 1000
* iceDensity (_real_) density of ice [kg/m3] | 1000
* specificThermalCapacityWater (_real_) specific thermal capacity of water [J/kg K] | 4188.0
* specificThermalCapacityIce (_real_) specific thermal capacity of ice [J/kg K] | 2117.0
* thermalConductivityWater (_real_) thermal conductivity of water [W/m K] | 0.6
* thermalConductivityIce (_real_) thermal conductivity of water [W/m K] | 2.29
* latentHeatFusion (_real_) latent heat of fusion of water [J/ kg] | 333700 
* referenceTemperatureInternalEnergy (_real_) reference temperature used to define the internal energy [K] | "273.15"

### Input and output files
* fileNovalue Value to indicate no data in the corresponding input file | "-9999"
* idfield (_str_) | "ID"
* pathGridShallow (_str_) | "$home/data/Grid_NetCDF/Case2_Grid_20m.nc"
* pathGridDeep (_str_) "$home/data/Grid_NetCDF/Case2_Grid_200m.nc"

## Boundary conditions

* topBCType (_str_) Type of the top boundary condition: "Top Neumann" the energy flux through the soil surface is assigned [W/m2] (positive: inflow, negative: outflow) "Top Dirichlet" the surface temperature is provided in [K] "Top HTC" the heat transfer coefficient boundary condition. This requires the heat transfer coefficient [W K-1] and air temperature [K] | "Top HTC"

* bottomBCType (_str_) Type of the bottom boundary condition: "Bottom Dirichlet" the water pressure value is assigned  "Bottom Neumann" you prescribe the water flux through the domain bottom  | "Bottom Neumann"

## Physical models
* sfccModel (_str_) Available SFCC models: "DallAmico", "Lunardini", "McKenzie",  "none" | "{Dall'Amico et al.,None}"

* equationStateModel (_str_)  Available state equation models: "Lunardini", "Soil", "Water"  | "{Soil Excess ice,rock}"

* soilThermalConductivityModel (_str_) Available thermal conductivity models for soil: "Johansen", "Lunardini",  "water"
 | "{Johansen,Rock}"

* thermalConductivityModel (_str_) | "{Arithmetic mean,Rock}"

* interfaceThermalConductivityModel (_str_) Available thermal conductivity models for excess ice: "Arithmetic mean", "Geometric mean",  "Harmonic mean",  "max",  "min" | "Harmonic mean"

