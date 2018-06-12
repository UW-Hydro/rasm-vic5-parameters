#!/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import rasterio
import os
import cartopy.crs as ccrs
from rasterio.warp import transform
from collections import OrderedDict
import netCDF4

# directory for soil files
direc = '/u/home/gergel/data/parameters/soil_data/geotiffs'

# dict of soil files to process
d = OrderedDict()
# add soil variables that will need to be processed
# %s needs to be filled in for soil layer, goes up to 7
#d['bulk_density'] = "BLDFIE_M_sl%s_1km_ll.tif" 
d['clay'] = "CLYPPT_M_sl%s_1km_ll.tif"
d['sand'] = "SNDPPT_M_sl%s_1km_ll.tif"
d['silt'] = "SLTPPT_M_sl%s_1km_ll.tif"
d['coarse'] = "CRFVOL_M_sl%s_1km_ll.tif"
d['bedrock'] = "BDTICM_M_1km_ll.tif"

d_varnames = OrderedDict()
d_varnames['bulk_density'] = "BLDFIE"
d_varnames['clay'] = "CLYPPT"
d_varnames['sand'] = "SNDPPT"
d_varnames['silt'] = "SLTPPT"
d_varnames['coarse'] = "CRFVOL"
d_varnames['bedrock'] = "BDTICM"

for key, items in d.items():
	if key != "bedrock":
		upper_range = 8
	else: 
		upper_range = 2
	for file_num in range(1, upper_range):
		filename = items %file_num
		file = os.path.join(direc, filename)
			
		# open as DataArray
		da = xr.open_rasterio(file)
	
		# compute lon/lat coords with rasterio.warp.transform
		ny, nx = len(da['y']), len(da['x'])
		x, y = np.meshgrid(da['x'], da['y'])

		# work with 1-D arrays 
		lon, lat = transform(da.crs, {'init': 'EPSG:4326'},
                     			     x.flatten(), y.flatten())
		lon = np.asarray(lon).reshape((ny, nx))
		lat = np.asarray(lat).reshape((ny, nx))
		da.coords['lon'] = (('y', 'x'), lon)
		da.coords['lat'] = (('y', 'x'), lat)

		# open as file object to get data
		dataset = rasterio.open(file)
		band = dataset.read(1)

		# create dataset to write to
		ds = xr.Dataset()
		ds['xc'] = xr.DataArray(lon, dims=('nj', 'ni'))
		ds['yc'] = xr.DataArray(lat, dims=('nj', 'ni'))
		ds[key] = xr.DataArray(band, dims=('nj', 'ni'), 
                                 	 coords={'lon': ds['xc'], 
                                         'lat': ds['yc']})
		# write dataset to netcdf
		netcdf_direc = "/u/home/gergel/data/parameters/soil_data/netcdfs"
		netcdf_filename = "%s_sl%s.nc" %(key, file_num)
		savepath = os.path.join(netcdf_direc, netcdf_filename)
		ds.to_netcdf(savepath, encoding={key: {'dtype': 'float'}},
             		     format='NETCDF4')
		
		
		# adjust file for using CDO
		fh = netCDF4.Dataset(savepath, 'r+')

		# fix xc attributes
		fh.variables['xc'].long_name = "longitude of grid cell center"
		fh.variables['xc'].units = "degrees_east"

		# fix yc attributes
		fh.variables['yc'].long_name = "latitude of grid cell center"
		fh.variables['yc'].units = "degrees_north"

		fh.variables[key].coordinates = "xc yc"

		fh.close()
