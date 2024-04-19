import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt


class Grid(object):

    def __init__(self, nc_grid_file):
        """ Representation of FreeThaw grid files """
        self.nc_grid_file = nc_grid_file
        self.nc = nc.Dataset(nc_grid_file, 'r')
        self.vi = self._valid_indices()
        self._vars = {}
        self._build_vars()

    def __del__(self):
        # close nc on deletion
        try:
            self.nc.close()
        except AttributeError:
            pass

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
        return fig

    def view_all(self):
        pass
    
    def parameter_names(self):
        V = [v for v in self.nc.variables if self.nc[v].dimensions == ('parameter',)]
        return V
    
    def depth_names(self):
        V = [v for v in self.nc.variables if self.nc[v].dimensions in [('z',), ('k',)]]
        return V
    
    def constant_names(self):
        dims = [d for d, v in self.nc.dimensions.items() if v.size == 1]
        V = [v for v in self.nc.variables if len(self.nc[v].dimensions) == 1 and self.nc[v].dimensions[0] in dims]
        return V
    
    def _build_vars(self):
        for n in self.parameter_names():
            self._vars[n] = self.nc[n][:].data[self.pid]

        for z in self.depth_names():
            self._vars[z] = self.nc[z][:].data[self.vi]

        for z in self.constant_names():
            self._vars[z] = self.nc[z][:]
    
    @property
    def vars(self):
        return list(self._vars.keys())
        

def _set_surface_height(grid, height):
    ''' Set the surface height of a grid to a given value'''
    with nc.Dataset(grid, 'a') as f:
        f['surfaceHeight'][:] = height
    print(f'surfaceHeight set to {round(height, 2)} m')


def _reset_surface_height(grid):
    '''Set the surface height of a grid according to the current column height (z)'''
    with nc.Dataset(grid, 'r') as f:
        zmax = max(f['z'][:])
    _set_surface_height(grid, zmax)


if __name__ == "__main__":
    pass    
"""
for f in Path("/scratch/s/stgruber/nbr512/NBFT/OMSPROJ/myriad").glob("sim*/output/_deep_spinup.nc"):
    print(f.parent.parent.name)
    _reset_surface_height(f)

for g in `ls sim*/output/_deep_spinup.nc`
do 
echo dirname dirname $g
cp $g $g.bak
done
"""