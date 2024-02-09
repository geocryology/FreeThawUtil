import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt


class Grid(object):

    def __init__(self, nc_grid_file):
        """ Representation of FreeThaw grid files """
        self.nc_grid_file = nc_grid_file
        self.nc = nc.Dataset(nc_grid_file)
        self.vi = self._valid_indices()
        self._vars = {}
        self._build_vars()

    def __repr__(self):
        type_ = type(self)
        module = type_.__module__
        qualname = type_.__qualname__
        return f"{module}.{qualname} ({self.nc_grid_file})"

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, key):
        return self._vars[key]

    def attrs(self):
        for a in self.nc.ncattrs():
            print(f"{a}: {self.nc.getncattr(a)}")

    def _valid_indices(self):
        return (self.nc['z'][:] != 0).data
    
    @property
    def pid(self):
        return self.nc['parameterID'][self.vi].data.astype('int64')
    
    def view(self, param, y='z'):
        """ Plot a parameter against depth or eta """
        fig, ax = plt.subplots()
        
        if y == 'z':
            ax.plot(self._vars[param], self._vars['z'])
            try:
                ax.set_ylabel(f"z [{self.nc['z'].units}]")
            except AttributeError:
                ax.set_ylabel(f"z [{self.nc['z'].unit}]")  # hopefuly this get standardized to 'units'

        elif y == 'eta':
            ax.plot(self._vars[param], -np.abs(self._vars['eta']))
            try:
                ax.set_ylabel(f"eta [{self.nc['eta'].units}]")
            except AttributeError:
                ax.set_ylabel(f"eta [{self.nc['eta'].unit}]")

        else:
            raise ValueError(f"Invalid y-axis: {y}")
        
        try:
            ax.set_xlabel(f"{param} [{self.nc[param].units}]")
        except AttributeError:
            ax.set_xlabel(f"{param}")
        
        if param == 'ic':
            # create vertical line at 273.15k
            ax.axvline(273.15, color='r', linestyle='--')
        fig.show()

    def view_all(self):
        pass
    
    def parameter_names(self):
        V = [v for v in self.nc.variables if self.nc[v].dimensions == ('parameter',)]
        return V
    
    def depth_names(self):
        V = [v for v in self.nc.variables if self.nc[v].dimensions in [('z',), ('k',)]]
        return V
    
    def constant_names(self):
        dims = [d for d, v in F.nc.dimensions.items() if v.size == 1]
        V = [v for v in F.nc.variables if len(F.nc[v].dimensions) == 1 and F.nc[v].dimensions[0] in dims]
        return V
    
    def _build_vars(self):
        for n in self.parameter_names():
            self._vars[n] = self.nc[n][:].data[self.pid]

        for z in self.depth_names():
            self._vars[z] = self.nc[z][:].data[self.vi]

        for z in self.constant_names():
            self._vars[z] = self.nc[z][:]
        

if __name__ == "__main__":
    D = nc.Dataset(r"C:\Users\Nick\Downloads\sim1063.tar\sim1063\output\_deep_spinup.nc")
    D = nc.Dataset(r"C:\Users\Nick\Downloads\sim1063.tar\sim1063\output\_deep_spinup.nc")
    e = nc.Dataset(r"C:\Users\Nick\Downloads\sim1063.tar\sim1063\input\deepGrid.nc")

    s = Grid(r"C:\Users\Nick\Downloads\sim1063.tar\sim1063\input\shallowGrid.nc")
    S = Grid(r"C:\Users\Nick\Downloads\sim1063.tar\sim1063\output\_shallow_spinup_SimulationBackUp.nc")
    D = Grid(r"C:\Users\Nick\Downloads\sim1063.tar\sim1063\output\_deep_spinup.nc")
    F = Grid(r"C:\Users\Nick\Downloads\sim1063.tar\sim1063\output\_Sim_complete_backup_SimulationBackUp.nc")

    S.view('ic', 'z')
    D.view('ic', 'z')

    S.view('ic', 'eta')
    D.view('ic', 'eta')
