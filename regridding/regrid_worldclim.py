#!/bin/env python

import configparser
import os 
from cdo import *
cdo = Cdo()

config = configparser.ConfigParser()
config.read('regridding.cfg')
domain_dir = config['Parameter Specs']['domain_file_dir']
domain_file = config['Parameter Specs']['domain_file']
domain = os.path.join(domain_dir, domain_file)
grid = config['Parameter Specs']['grid']
res = config['Parameter Specs']['res']
outdir = config['Parameter Specs']['output_dir']

# process WorldClim NetCDFs by cropping them and then regridding them

clim_vars = ["tavg","prec"]

months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]


for clim_var in clim_vars:
	for month in months:

		filename = "%s_%s.nc" %(clim_var, month)
		file = os.path.join(config['WorldClim']['netcdf_dir'], filename) 		

		# crop file
		crop_filename = "cropped_%s_%s.nc" %(clim_var, month)
		crop_file = os.path.join(outdir, crop_filename)
		#cdo.sellonlatbox("-180,180,15,90", input="-selname,Band1 %s" %filename, output=crop_file)
		cdo.sellonlatbox("-180,180,15,90", input=file, output=crop_file)

		# regrid file
		tmp1 = os.path.join(outdir, "%s_%s_tmp.nc" %(clim_var, month))
		tmp2 = os.path.join(outdir, "%s_%s_%s_tmp.nc" %(clim_var, month, grid))
		regrid_file = os.path.join(outdir, "%s_%s_%s.nc" %(clim_var, month, grid))

		# set fillvalues to missing values to avoid incorrect remapping of coastal gridcells, 
		# solution adapted from https://code.mpimet.mpg.de/boards/2/topics/6172?r=6199
		cdo.setvrange('-1000,1000', input=crop_file, output=tmp1)
		cdo.setmisstonn(input=tmp1, output=tmp2)

		# remap both land and ocean gridcells so that coastal gridcells are assigned valid values
		cdo.remapnn(domain, input=tmp2, output=regrid_file)
	
		# remove intermediate files
		rm_files = [crop_file, tmp1, tmp2]
		for file_obj in rm_files:
			os.remove(file_obj)
