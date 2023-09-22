## Understanding the `.sim` file
In the OMS Framework, the model is best thought of not as a black box with inputs and outputs, but instead, a box of LEGO: multiple components that fit together.  Each component has its own inputs and outputs which can be piped together

The `.sim` file describes how these components are connected. 

Basic mathematical expressions are allowed
```groovy
def writingFrequency = 60 * 24
```

There are  four components to a typical `.sim` file,
```groovy
// # 1
// variable definition
def variable = 1

solver = OMS3.sim(name: "spinup_two_step_procedure", {
resource "$oms_prj/lib"
	model(while : "reader_data_topBC_transient_simulation.doProcess"  ){
		components {
// Aliasing java classes
}
parameter{
// Assigning parameters
}

```
## Generating Output
To generate output netcdf files, you must use one of the following components
* `freethaw1dxice.netcdf.WriteNetCDFFreeThawXice1DDouble` All variables 
* `freethaw1dxice.netcdf.WriteNetCDFFreeThawXice1DDoubleAggregated` 
*	`freethaw1dxice.netcdf.WriteNetCDFFreeThawXice1DSimulationBackUpLastTimeStep`
*	`freethaw1dxice.netcdf.WriteNetCDFFreeThawXice1DDiscreteDepthCoordinate` 
*	`freethaw1dxice.netcdf.WriteNetCDFFreeThawXice1DDiscreteHeightCoordinate` Variables at height coordinates specified by `mySpatialCoordinate`
