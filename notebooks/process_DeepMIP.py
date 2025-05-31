#!/Users/gam24/anaconda3/envs/core/python

import xarray as xr
import xesmf
import numpy as np
import utils.geo as geo
import glob
import os

variable = 'vo'
modelconfigs = ['CESM/CESM1.2_CAM5']#['COSMOS/COSMOS-landveg_r2413','CESM/CESM1.2_CAM5','GFDL/GFDL_CM2.1','INMCM/INM-CM4-8','MIROC/MIROC4m','NorESM1_F','HadCM3/HadCM3BL_M2.1aN','HadCM3/HadCM3B_M2.1aN']
regrid = True
overwrite = True
averaging = 'mean'

# consistent file settings
rootdir = '/Volumes/DeepMIP_Model_Output_read/DeepMIP-Eocene/User_Model_Database_v1.0'

### VARIABLE NAMES
latnames = ['TLAT','lat','geolat_t','latitude','nav_lat','latitude_1','ULAT','VLAT']
lonnames = ['TLONG','lon','geolon_t','longitude','nav_lon','longitude_1','ULONG','VLONG']
timenames = ['month','time','t','time_counter']
znames = ['z_t','st_ocean','lev','depth','depth_1','level','plev','p','sfc']

### LOAD PREDEFINED REGULAR GRID
# created via generate_grid.py
if variable in ['tos','thetao','so','sos','uo','vo']:
    dlon,dlat = 1,1
    zlevel = 'depth'
elif variable in ['tas','ta']:
    dlon,dlat = 3,2
    zlevel = 'pressure'
gridname = str(dlon)+'x'+str(dlat)
grid = xr.open_dataset('../data/processed/regridded/grid_'+gridname+'_'+zlevel+'.nc')

for modelconfig in modelconfigs:
    try:
        [model,config]=modelconfig.split('/')
    except:
        model,config = modelconfig, modelconfig
    experiment = '*'
    version = 'v1.0'
    filename_pre = '-'.join([config,experiment,variable,version])
    filename = '.'.join([filename_pre,averaging,'nc'])
    # file structure error correction for NorESM
    if model=='NorESM1_F':
        path = '/'.join([rootdir,model,experiment,version,filename])
    else:
        path = '/'.join([rootdir,model,config,experiment,version,filename])

    # find paths
    paths = glob.glob(path)
    if not paths:
        print('No files at '+path)
        continue
    # correction for additional files present in COSMOS
    if model=="COSMOS":
        paths = [path for path in paths if 'r122' not in path]

    ### PREPROCESS FUNCTION
    def preprocess(ds):
        path_elements = ds.encoding["source"].split('/')
        model = path_elements[5]
        print(model,end=', ')
        if model=='NorESM1_F': # muddled file structure for NorESM
            nconfig = 5
            nexperiment = 6
        else:
            nconfig = 6
            nexperiment = 7
        config = path_elements[nconfig]
        experiment = path_elements[nexperiment]
        print(config,end=', ')
        print(experiment)

        # change variable names
        # lat
        lat = list(set(latnames).intersection(ds.coords))[0]
        if lat!='lat':
            ds = ds.rename({lat:'lat'})
        # lon
        lon = list(set(lonnames).intersection(ds.coords))[0]
        if lon!='lon':
            ds = ds.rename({lon:'lon'})
        # depth/pressure
        if len(list(set(znames).intersection(ds.coords)))>0:
            zdim = True
            z = list(set(znames).intersection(ds.coords))[0]
            if z!='z':
                ds = ds.rename({z:'z'})
        else:
            zdim=False
        # time
        time = list(set(timenames).intersection(ds.coords))[0]
        if time!='time':
            ds = ds.rename({time:'time'})
        if (model=='NorESM1_F') & (variable in ['thetao','tos','so','sos']): # no seasonal info available for NorESM ocean
            timearray = np.arange(1)
        else:
            timearray = np.arange(12)
        ds = ds.assign_coords({'time':timearray})

        if regrid:
            ## horizontal regrid
            # initiate regridder
            regridder = xesmf.Regridder(ds,grid,'bilinear', periodic=True)
            # regrid dataset
            ds = regridder(ds)

            ## vertical regrid
            if zdim:
                if (config=='CESM1.2_CAM5'):
                    ds['z']=ds['z']*1e-2 # conversion from cm
                ds = ds.interp({'z':grid['z']})

        # place experiment as distinct dimension
        ds = ds.squeeze().expand_dims({'experiment':[experiment]})
        # drop all other variables
        ds = ds[variable].to_dataset()

        return ds

    ### OPEN DATASET
    ds = xr.open_mfdataset(paths,preprocess=preprocess,decode_times=False)

    ### SAVE
    savename = '.'.join([config,variable,averaging,gridname,'nc'])
    if regrid:
        savepath = '../data/processed/regridded/'+savename
    else:
        savepath = '../data/processed/native/'+savename
    if overwrite:
        try:
            os.remove(savepath)
        except OSError:
            pass
    ds = ds.compute()
    ds.to_netcdf(savepath,mode='w')