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
import configparser

config = configparser.ConfigParser()
config.read('regridding.cfg')

# directory for World Clim data
# downloaded from World Clim site, http://worldclim.org/version2, 10min global data, 
# 1 file for each month, 1970-2000 averages
direc = config['WorldClim'['geotiff_dir']
netcdf_direc = config['WorldClim']['netcdf_dir']

# dict of temp and precip files to process
d = OrderedDict()
# add soil variables that will need to be processed
# %s needs to be filled in for month, goes up to 12
d['prec'] = "wc2.0_10m_prec_%s.tif"
d['tavg'] = "wc2.0_10m_tavg_%s.tif"

month_nums = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

for key, items in d.items():
	for i, month_num in enumerate(month_nums):
		filename = items %month_num
		subdir = "wc2.0_10m_%s" %key
		file = os.path.join(direc, subdir, filename)
			
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
		netcdf_filename = "%s_%s.nc" %(key, month_num)
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
