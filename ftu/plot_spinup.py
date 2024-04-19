import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

def show_spinup(shallow_spinup:str):
    """Plot the spinup of a shallow model run
    
    Parameters
    ----------
    shallow_spinup : str
        Path to the shallow spinup file

    
    """
    with nc.Dataset(shallow_spinup) as nss:
        var_t = nss['time']
        time = nc.num2date(var_t[:], var_t.units, 'standard', 
                        only_use_cftime_datetimes=False, only_use_python_datetimes=True)
        temp = nss['mean_temperature_in_ground'][:] - 273.15
        h = nss['height'][:]

    fig, axs = plt.subplots(2,2)

    # lowest depth
    LD = axs[0,0]
    LD.plot(time, temp[:,-1])

    # last p% of spinup
    # lowest depth
    LDp = axs[1,0]
    p = 90
    LDp.plot(time[(p*(len(time) // 100)):], temp[(p*(len(time) // 100)):,-1])

    # profile evolution (n=10 steps)
    n=10
    cmap = cm.get_cmap('winter')
    clist = cmap(np.arange(0,1,1/10))
    PE = axs[0,1]
    tPE = time[::len(time)//n][:n]
    TPE = temp[::len(time)//n,][:10,]
    for i in range(n):
        PE.plot(TPE[i,:], h, color=clist[i], alpha=0.5)

    # profile evolution (n=10 steps)
    PEp = axs[1,1]
    lastP = (p*(len(time) // 100))
    tPEp = time[lastP:][::len(time[lastP:])//n][:n]
    TPEp = temp[lastP:,][::len(time[lastP:])//n,][:n,]
    for i in range(n):
        PEp.plot(TPEp[i,:], h, color=clist[i], alpha=0.5)

    fig.show()

    return fig


def profile_evo(depths, times, values, P:int=100, n:int=10):
    """ Plot evolution of temperature profiles over time
    
    Parameters
    ----------
    depths : array-like
        Depths of the temperature profile
    times : array-like
        Times of the temperature profile
    values : array-like
        Temperature values of the temperature profile
    P : int, optional
        Percentage of the time series to plot, starting from the end, by default 100
    n : int, optional  
        Number of profiles to plot, by default 10
    """
    # profile evolution (n=10 steps)
    cmap = cm.get_cmap('winter')
    clist = cmap(np.arange(0,1,1/10))

    fig, axs = plt.subplots()
    p = 100 - P
    lastP = (p*(len(times) // 100))
    true_depths = -np.abs(depths)
    plot_times = times[lastP:][::len(times[lastP:])//n][:n]
    plot_temps = values[lastP:,][::len(times[lastP:])//n,:][:n,]
    for i in range(n):
        axs.plot(plot_temps[i,:], true_depths, color=clist[i], alpha=0.5, label=f"{plot_times[i].year}")
    axs.legend(fontsize="8")
    axs.vlines(0, ymin=min(true_depths), ymax=max(true_depths), linewidth=0.5, color='black')

    fig.show()

profile_evo(df_dpt.columns, df_dpt.index, df_dpt.values  -273.15)