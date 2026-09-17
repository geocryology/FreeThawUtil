import pandas as pd
import datetime
from ftu import read_oms_table, write_oms


# creation of long timeseries data for spin-up


def repeat_timeseries(df:pd.DataFrame,
                      freq="D",
                      nyear=30,
                      mcycles=10) -> pd.DataFrame:
    """ repeat the first N years of a timeseries M times """
    dt = df['timestamp'][1] - df['timestamp'][0]
    cutoff = df.timestamp[0] + pd.Timedelta(f"{nyear * 365}D")
    rep = df[(df.timestamp <= cutoff)]
    spinup_period = pd.concat([rep] * mcycles)
    output = pd.concat([spinup_period, df], ignore_index=True)
    
    try:
        output['timestamp'] = pd.date_range(end=output.timestamp.iloc[-1], freq=freq, periods=output.shape[0])
    except Exception:
        if freq != "D":
            raise RuntimeError("can only do daily now")
        output['timestamp'] = dt_daterange(output.timestamp.iloc[-1].to_pydatetime().date(), output.shape[0])
    return output


def dt_daterange(end_date:datetime.date, length) -> list[str]:
    # Compute start date
    start_date = end_date - datetime.timedelta(days=length - 1)

    # Generate date list
    dates = [(start_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d").rjust(10, "0") for i in range(length)]

    return dates



def extend_oms(old_oms: str,
               new_oms: str,
               freq="D",
               nyear=30,
               mcycles=10,
               time_index=0,
               time_format="%Y-%m-%d %H:%M") -> None:
    
    t = read_oms_table(old_oms)
    df = t.data
    df.iloc[:,time_index] = pd.to_datetime(df.iloc[:,time_index], format=time_format)
    extended = repeat_timeseries(df=df,
                                 freq=freq,
                                 nyear=nyear,
                                 mcycles=mcycles)

    try:
        dat = pd.DatetimeIndex(extended.iloc[:, time_index], freq=freq)
    except Exception:
        if freq != "D":
            raise RuntimeError("can only do daily now")
        dat = [datetime.datetime.strptime(s, "%Y-%m-%d") for s in extended.iloc[:, time_index]]

    write_oms(filename=new_oms,
              dates=dat,
              data=extended.drop(extended.columns[time_index], axis=1).values,
              infer_dtypes=True)

