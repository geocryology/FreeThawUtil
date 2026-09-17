import pandas as pd
import numpy as np
from scipy.signal import detrend

def create_future(air_temp: pd.Series, 
                  future_trend: pd.Series,
                  final_year:int, 
                  seed:int=42) -> pd.Series:
    """ 
    air_temp : pd.Series
        Daily air temperature data.  Index is DatetimeIndex 
    future_trend : pd.Series
        future trend data. Annual temperature . Index is DatetimeIndex. Values will be differenced to the last year of air_temp to create offsets
    n_years: int
        how many years into the future should data be constructed
    seed: int
        random seed for reproducibility

    Returns
    -------
    pd.DataFrame
        future air temperature data. Index is DatetimeIndex

    Details
    -------
    1. detrend air_temp
    2. calculate standard deviation of yearly means of detrended air_temp (sd_ym)
    2. for each year in n_years, take year of data from detrended air_temp and add normally distributed offset
    3. find the last year of air_temp data (last_year)
    4. turn future_trend into offsets by differencing with (i.e. future_trend = future_trend - future_trend[last_year])
    5. add future_trend to future air_temp data
    """
    np.random.seed(seed)
    
     # 1. Detrend air_temp using scipy.signal.detrend
    detrended_values = detrend(air_temp.values)
    detrended_air_temp = pd.Series(detrended_values, index=air_temp.index)
    
    # 2. Calculate mean T of last Q years
    Q=6
    mt = air_temp[-365*Q:].mean()
    detrended_air_temp += mt
    
    # 3. Generate synthetic future years
    last_year = air_temp.index[-1].year
    n_years = final_year - last_year
    future_years = range(last_year + 1, last_year + 1 + n_years)
    sampled_years = np.random.choice(air_temp.index.year.unique(), size=n_years, replace=True)

    future_data = []
    for future_year, sampled_year in zip(future_years, sampled_years):
        sampled_data = detrended_air_temp[detrended_air_temp.index.year == sampled_year].copy()  # 365 or 366 days
        date_range = pd.date_range(start=f"{future_year}-01-01", end=f"{future_year}-12-31", freq="D")
        nan_series = pd.Series(np.nan, index=date_range)
        
        if len(sampled_data) == len(nan_series):
            nan_series[:] = sampled_data.values
        elif len(sampled_data) > len(nan_series):
            nan_series[:] = sampled_data[:len(nan_series)].values
        else:
            nan_series[:len(sampled_data)] = sampled_data.values
        
        sampled_data = nan_series.ffill()
        future_data.append(sampled_data)
    
    future_air_temp = pd.concat(future_data)
    
    # 4. Process future_trend offsets
    ft = future_trend.copy().resample("Y").mean()
    future_trend_offset = ft - ft[ft.index.year == last_year].values
    future_trend_offset = future_trend_offset[future_trend_offset.index.year >= last_year]

    # 5. Add trend to the synthetic future data
    future_air_temp += future_trend_offset.resample("D").ffill()
    
    return future_air_temp
