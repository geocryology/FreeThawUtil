import netCDF4 as nc
import numpy as np


class AllVariables:

    def __init__(self, file):
        self.file = file
        self.ds = nc.Dataset(file)
        self.ix = _valid_indices_2d(self.ds['height'][:])

    def __getitem__(self, key):
        raw = self.ds[key]
        var = self.__returnvar(raw)
        return var

    def get(self, var, atdepth=None, atheight=None):
        """ Return value of variable at desired depth or height """
        if atdepth:
            return _get_var_at_depth(self[var], self['height'], atdepth)
        elif atheight:
            return _get_var_at_height(self[var], self['height'], atheight)
        else:
            return self[var]
        
    @property
    def time(self):
        """ Time values """
        timevar = self.ds['time']
        times = nc.num2date(timevar[:], timevar.units, 'standard',
                            only_use_python_datetimes=True, 
                            only_use_cftime_datetimes=False)
        return times

    @property
    def vars(self) -> list:
        """ List of variables in file """
        return list(self.ds.variables)
    
    def __returnvar(self, var: nc.Variable) -> np.ndarray:
        if _dim_is_time_k(var):
            return _subsample_valid(var, self.ix)
        elif _dim_is_k(var):
            return var[:]
        elif _dim_is_time(var):
            return var[:]
        else:
            raise ValueError("Variable does not have a valid dimension")


def _dim_is_k(var: nc.Variable) -> bool:
    return var.dimensions == ('k',)


def _dim_is_time_k(var: nc.Variable) -> bool:
    return var.dimensions == ('time', 'k')


def _dim_is_time(var: nc.Variable) -> bool:
    return var.dimensions == ('time',)
     

def _valid_indices_1d(arr: np.ndarray) -> np.ndarray:
    """ 1 time slice array (k,)"""
    isn = np.isnan(arr)
    is0 = arr == 0
    valid = ~(isn | is0)
    return valid


def _valid_indices_2d(arr: np.ndarray) -> np.ndarray:
    """ 2d array (time,k)"""
    valid = np.apply_along_axis(_valid_indices_1d, 1, arr)
    return valid


def _subsample_valid(arr: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """ 2d array (time,k,)"""
    k=np.apply_along_axis(np.sum, 1, valid)
    i=len(k)
    j=max(k)
    
    if not np.all(k == j):
        raise ValueError("Not all time slices have the same number of valid points")
    
    subsample = np.empty((i,j))
    
    for i, v in enumerate(valid):
        subsample[i,:] = arr[i,:][v]
    
    return subsample


def _get_var_at_height(var: np.ndarray, height: np.ndarray, h: float) -> np.ndarray:
    """ 2d array (time,)"""
    return None

def _get_var_at_depth(var: np.ndarray, depth: np.ndarray, d: float) -> np.ndarray:
    """ 2d array (time,)"""
    return None

