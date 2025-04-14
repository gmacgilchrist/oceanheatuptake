#!/Users/gam24/anaconda3/envs/core/python

import xarray as xr
import numpy as np
import utils.geo as geo

dlon,dlat = 3,2
zlevel = 'pressure'

grid = xr.Dataset()
lons = dlon/2 + np.arange(0,360,dlon)
lats = dlat/2 -90 + np.arange(0,180,dlat)
grid['lon'] = xr.DataArray(data=lons, dims=('x'), coords={'x':lons})
grid['lat'] = xr.DataArray(data=lats, dims=('y'), coords={'y':lats})
ds,xgrid = geo.get_xgcm_horizontal(grid,
                                   axes_dims_dict={'X':'x','Y':'y'},
                                   periodic=['X'],
                                   boundary_discontinuity={'x':360})

if zlevel == 'depth':
    target_zs = np.array([5.000000e+00, 1.500000e+01, 2.500000e+01, 3.500000e+01, 4.500000e+01,
                           5.500000e+01, 6.500000e+01, 7.500000e+01, 8.500000e+01, 9.500000e+01,
                           1.050000e+02, 1.150000e+02, 1.250000e+02, 1.350000e+02, 1.450000e+02,
                           1.550000e+02, 1.650000e+02, 1.750000e+02, 1.850000e+02, 1.950000e+02,
                           2.050000e+02, 2.150000e+02, 2.250000e+02, 2.361228e+02, 2.506000e+02,
                           2.706208e+02, 2.983049e+02, 3.356756e+02, 3.846343e+02, 4.469366e+02,
                           5.241706e+02, 6.177363e+02, 7.288285e+02, 8.584215e+02, 1.007257e+03,
                           1.175835e+03, 1.364406e+03, 1.572971e+03, 1.801279e+03, 2.048829e+03,
                           2.314879e+03, 2.598456e+03, 2.898365e+03, 3.213206e+03, 3.541390e+03,
                           3.881162e+03, 4.230621e+03, 4.587743e+03, 4.950409e+03, 5.316429e+03])
    top = target_zs[-1]+np.diff(target_zs)[-1]
    bottom = 0
elif zlevel == 'pressure':
    target_zs = np.array([1000.,  950.,  900.,  850.,  800.,  750.,  700.,  650.,  600.,  550.,
                                    500.,  450.,  400.,  350.,  300.,  250.,  200.,  150.,  100.,   70.,
                                     50.,   30.,   20.,   10.])
    top = 5
    bottom = 1050
mid_zs = np.append(bottom,0.5*(target_zs[:-1]+target_zs[1:]))
mid_zs = np.append(mid_zs,top)
dz = xr.DataArray(np.diff(mid_zs),dims='z',coords={'z':target_zs})

grid['area'] = ds['rC']
grid['dz'] = dz
grid['volume'] = grid['area']*grid['dz']

gridname = str(dlon)+'x'+str(dlat)
grid.to_netcdf('../data/processed/regridded/grid_'+gridname+'_'+zlevel+'.nc')