import netCDF4 as nc
from ftu.simfile import FreeThawSim, resolve, nq
from pathlib import Path


def get_last_time(ncdf_file):
    with nc.Dataset(ncdf_file) as ncdf:
        last_t = nc.num2date(ncdf['time'][-1], ncdf['time'].units, 'standard',
                                only_use_python_datetimes=True, 
                                only_use_cftime_datetimes=False)
    return last_t


def update_incomplete_spinup(simfile:str, 
                             oms_prj:str,
                             tStart:str="tStart", 
                             pathShallowSpinupBackup:str="pathShallowSpinupBackUp",
                             pathShallowSpinupMeanT:str="pathShallowSpinupMeanT",
                             pathGridShallow:str="pathGridShallow"):
    """Updates a simfile to re-start after an incomplete spinup """
    sim = FreeThawSim(simfile)
    backup = sim.get_variable_line(pathShallowSpinupBackup)
    spinupT = sim.get_variable_line(pathShallowSpinupMeanT)

    if (spinupT is None)  or (backup is None):
        raise ValueError("Could not find simfile entry for tStart or shallow spinup file")
    
    ncdf_file = resolve(sim, spinupT.get('value'), oms_prj)
    last_t = get_last_time(ncdf_file)
    
    sim.set_variable(tStart, last_t.strftime("%Y-%m-%d %H:%M")) # set tstart as last t
    sim.set_variable(pathGridShallow, nq(backup.get('value'))) # change read path to backup file
    
    sim.write(simfile)




for sim in [10109, 1037, 1061, 1086, 1087, 109, 37, 61, 79]:
    t = get_last_time(f"/home/nbr512/scratch/NBFT/OMSPROJ/myriad/sim{sim}/output/_Sim_complete_discrete_height_0000.nc")
    print(f"{sim} = {t.strftime(r'%Y-%m-%d %H:%M')}")

import shutil

for sim in [10109, 1037, 1061, 1086, 1087, 109, 37, 61, 79]:
    shutil.copy("/home/nbr512/storage/projects/metrics/OMS_Project_FreeThawXice1D-0.9.6/simulation/metrics_resume.sim",
                f"/home/nbr512/scratch/NBFT/OMSPROJ/myriad/sim{sim}/sim{sim}.sim.restart")
    
'''
restart incomplete sims from the end of spinup (workaround)
for s in 61 37 79 109
do
sed -r -i 's_def tStart = .*_def tStart = "1978-01-01 00:00"_' sim$s/sim$s.sim 
mv "sim$s/output/_deep_spinup.nc" "sim$s/output/_pre-spunup.nc" 
sed  -r -i 's#("reader_NetCDF_transient_simulation.gridFilename") .*#\1 "$outDir/_pre-spunup.nc"#' sim$s/sim$s.sim  
done
'''



update_incomplete_spinup("/home/nbr512/scratch/NBFT/OMSPROJ/myriad/sim85/sim85.sim", "/home/nbr512/scratch/NBFT/OMSPROJ")
update_incomplete_spinup("/home/nbr512/scratch/NBFT/OMSPROJ/myriad/sim1085/sim1085.sim", "/home/nbr512/scratch/NBFT/OMSPROJ")