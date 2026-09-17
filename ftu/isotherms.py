import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def _all_negative(T: np.ndarray):
    ''' are all values negative in vector
    T : np.ndarray
    '''
    return np.less_equal(T, 0).all()


def _all_negative_at_z(T: np.ndarray):
    ''' are all temperatures negative at z
    T : np.ndarray
        (time, z)
    '''
    return np.apply_along_axis(_all_negative, 0, T)
 
    
def _all_negative_z(T: np.ndarray, z: np.ndarray) -> np.ndarray:
    mask = _all_negative_at_z(T)
    if mask.any():
        return z[mask]
    else:
        return np.array([], dtype='float64')
     
        
def _all_positive(T: np.ndarray):
    ''' are all values positive in vector
    T : np.ndarray
    '''
    return np.greater(T, 0).all()


def _all_positive_at_z(T: np.ndarray):
    ''' are all temperatures positive at z
    T : np.ndarray
        (time, z)
    '''
    return np.apply_along_axis(_all_positive, 0, T)
 
    
def _all_positive_z(T: np.ndarray, z: np.ndarray) -> np.ndarray:
    mask = _all_positive_at_z(T)
    if mask.any():
        return z[mask]
    else:
        return np.array([], dtype='float64')


def _has_no_isotherms_above_zc(i0: np.ndarray, zc:float=0):
    '''Check for the existance of time at which no isotherms above zc '''
    _i0 = i0.copy()
    _i0[_i0 < zc] = np.nan

    def _all_nan(arr):
        return np.isnan(arr).all()
    
    return np.apply_along_axis(_all_nan, 1, _i0)
    

    
def _ith_isotherm_above_z(iso: np.ndarray, i:int, zc:float):
    ''' get the depth of the (1-indexed) ith isotherm above a cutoff depth 
    '''
    if i==0:
        raise ValueError("i is 1-indexed")
        
    i0 = iso.copy()
    i0[i0 < zc] = np.nan
    i0[i0.mask] = np.nan  # handles case where only 1 isotherm above otherwise masked values get unmasked

    def _get_ith(arr):
        arr = np.sort(arr)  # numpy sort puts nans at end
        return arr[i-1]
        
    return np.apply_along_axis(_get_ith, 1, i0)


def _isotherm_talik_test(iso:np.ndarray, pf_depth:float):
    ''' test for a suprapermafrost talik by comparing the depths of the two isotherms directly above the permafrost'''    
    i01 = _ith_isotherm_above_z(iso, 1, pf_depth)
    i02 = _ith_isotherm_above_z(iso, 2, pf_depth)
    
    if np.nanmin(i02) > np.nanmax(i01):
        return 0.5 * (np.nanmin(i02) + np.nanmax(i01))
    else: 
        return np.nan


def _gets_isotherm(T, z, iso, sh, za_returner):
    i0 = iso.copy()
    oob = i0 > (np.tile(sh, (i0.shape[1],1)).transpose())
    i0.mask = i0.mask | oob

    pf_z = _all_negative_z(T, z)
    talik_z = _all_positive_z(T, z)
    
    if len(pf_z) > 0:  # check if we have observations of 'permafrost'
        pf_middle = (0.5) *(max(pf_z) + min(pf_z)) # cenral permafrost 'node'
        i0.mask = i0.mask | (i0 < min(pf_z))  # ignore isotherms below pf
        isotherm_talik = _isotherm_talik_test(i0, pf_middle)
        
        if _has_no_isotherms_above_zc(i0, pf_middle).any() or np.isnan(isotherm_talik):  # check for existence of no isotherms above pf
            za = za_returner(_ith_isotherm_above_z(i0, 1, pf_middle - 0.01))
            # print(f"take min z above pf_middle ")
            return za
        
        else:  # always at least 1 isotherm above pf
            
            if ~np.isnan(isotherm_talik):  # check if any 'talik' nodes above 'permafrost'
                za = za_returner(_ith_isotherm_above_z(i0, 2, pf_middle - 0.01))
                # print(f"take second lowest z above pf_middle ({za})")
                return za
                
            else:  # cannot identify any 'talik' nodes above permafrost
                # import pdb;pdb.set_trace()
                raise NotImplementedError("cannot identify any 'talik' nodes above permafrost")
                
    else:  # no observations of 'permafrost'
        raise NotImplementedError("missing observations within permafrost")
           

def _zr_min(iso):
    ''' returns the minimum of the selected isotherm'''
    return np.nanmin(iso)


def _zr_all(iso):
    ''' returns the whole isotherm '''
    return iso
    

def get_single_alt(T, z, iso, sh):
    return _gets_isotherm(T, z, iso, sh, _zr_min)


def get_continuous_alt(T, z, iso, sh):
    return _gets_isotherm(T, z, iso, sh, _zr_all)


def extract_alt_isotherm(T, t, iso, z, hs):
    """ 
    data must be yearly 

    Parameters
    ----------
    T : np.ndarray
        yearly temperature data (time,z)
    t : np.ndarray
        timestamps
    iso : np.ndarray
        isotherm depths (time, n)
    z : np.ndarray
        height values for T
    hs : np.ndarray
        ground surface height
    """
    T = ensure_units_celcius(T)

    # make empty array
    res = np.empty(len(t))
    res[:] = np.nan
    
    # split into yearly bins
    for n in range(len(t) // 365):
        try:
            print(f"[{n}] year {t[365*n].year}")
            res[n*365:(n+1)*365] = get_continuous_alt(T[n*365:(n+1)*365], z, iso[n*365:(n+1)*365], hs[n*365:(n+1)*365])
        except NotImplementedError as e:
            res[n*365:(n+1)*365] = np.nan
            print(str(e))
            
    df = pd.Series(index=t, data=res, name='isotherm')
    try:
        alt = df.rolling("365D", min_periods=np.nan).min()
    except ValueError:  # version differences in pandas
        alt = df.rolling("365D", min_periods=None).min()
    
    return alt
            

def extract_alt_isotherm_depth(T, t, iso, depth, hs):
    """ 
    data must be yearly.  approximation of depth to height is done by assuming constant height within year

    Parameters
    ----------
    T : np.ndarray
        yearly temperature data (time,z)
    t : np.ndarray
        timestamps
    iso : np.ndarray
        isotherm depths (time, n)
    depth : np.ndarray
        depth values for T (approximated as constant-height within year)
    hs : np.ndarray
        ground surface height
    """
    T = ensure_units_celcius(T)
    # make empty array
    res = np.ma.array(np.empty(len(t)))
    res[:] = np.nan
    
    z = depth_to_height(depth, hs)
    # split into yearly bins
    ti = pd.DatetimeIndex(t)
    for Y in range(t[0].year, t[-1].year):
        ix = (ti.year == Y)
        try:
            print(f"{Y}")
            res[ix] = get_continuous_alt(T[ix], z[ix, :][-1, :], iso[ix], hs[ix])
        except NotImplementedError as e:
            print(str(e))

    df = pd.Series(index=t, data=res, name='isotherm')
    df[df==0] = pd.NA

    alt = df.rolling("365D", min_periods=1).min()
    hdf = pd.DataFrame(index=t, data={'hs':hs})
    res = pd.merge(alt, hdf, how='inner', left_index=True, right_index=True)
    res['alt'] = res['hs'] - res['isotherm']
    return res[['alt']]


def depth_to_height(d: np.ndarray, hs: np.ndarray):
    """ 
    Parameters
    ----------
    d : np.ndarray
        observation depth below surface (d,)
    hs : np.ndarray
        time-depentent surface height (t,)
        
    Returns
    -------
    np.ndarray
        observation height (time, z)
    """
    _hs = np.tile(hs, ((d.shape[0],1))).transpose()
    _d = np.tile(d, ((hs.shape[0],1)))
    h = _hs - _d
    return h

def ensure_units_celcius(T: np.ndarray):
    if np.nanmax(T) > 100:
        return T - 273.15
    else:
        return T
