#!/bin/env python 

import configparser
import os 
import numpy as np
from cdo import *
cdo = Cdo()

cwd = os.getcwd()
print(cwd)

config = configparser.ConfigParser()
config.read(os.path.join(cwd, 'regridding.cfg'))
domain_dir = config['Parameter Specs']['domain_file_dir']
domain_file = config['Parameter Specs']['domain_file']
domain = os.path.join(domain_dir, domain_file)
grid = config['Parameter Specs']['grid']
res = config['Parameter Specs']['res']
outdir = config['Parameter Specs']['output_dir']

dir = config['Soil Data']['netcdf_dir']

# process soil grid NetCDFs by cropping them and then regridding them
# declare -a soil_variables=("bulk_density" "organic_fract")
soil_variables = ["clay", "sand", "silt", "coarse", "bulk_density", "organic_fract"]

for soil_var in soil_variables:
	# number of soil layers in dataset (7) + 1
	nlayers = 8
	
	for layer in np.arange(1, 8): 

		filename = os.path.join(dir, '%s_sl%s.nc' %(soil_var, str(layer)))		

		# crop file
		crop_file = os.path.join(dir, 'cropped_%s_sl%s.nc' %(soil_var, str(layer)))
		cdo.sellonlatbox("-180,180,15,90", input=filename, output=crop_file)

		# regrid file
		tmp1 = os.path.join(dir, '%s_sl%s_tmp.nc' %(soil_var, str(layer)))
		tmp2 = os.path.join(dir, '%s_sl%s_%s_tmp.nc' %(soil_var, str(layer), grid))
		regrid_file = os.path.join(outdir, '%s_sl%s_%s.nc' %(soil_var, str(layer), grid))
		
		# set fillvalues to missing values to avoid incorrect remapping of coastal gridcells, 
		# solution adapted from https://code.mpimet.mpg.de/boards/2/topics/6172?r=6199
		# set valid ranges for each soil variable and remaining values to missing values
		if soil_var == "bulk_density":
			# bulk density (kg/m3)
			vmin = 50
			vmax = 3000
		elif soil_var == "organic_fract":
			# soil organic carbon content (g/kg)
			vmin = 0
			vmax = 500
		else:
			# sand, silt, coarse, clay content, volumetric (%)
			vmin = 0
			vmax = 100

		vrange = '%s,%s' %(str(vmin), str(vmax))
		cdo.setvrange(vrange, input=crop_file, output=tmp1)
		cdo.setmisstonn(input=tmp1, output=tmp2)

		# remap both land and ocean gridcells so that coastal gridcells are assigned valid values 
		# use nearest neighbor remapping for all soil variables
		cdo.remapnn(domain, input=tmp2, output=regrid_file)
	
		# remove temp files
		rm_files = [crop_file, tmp1, tmp2]
		for file_obj in rm_files:
			os.remove(file_obj)
