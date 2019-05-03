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


filename = os.path.join(config['GTOPO']['dir'], 
			config['GTOPO']['filename'])
		
# crop file
crop_file = os.path.join(outdir, 'cropped_dem.nc')
cdo.sellonlatbox("-180,180,16.5,90", input="-selname,Band1 %s" %filename, output=crop_file)

# regrid file
regrid_file = os.path.join(outdir, 'sdat_10003_1_20180525_151136146_%s.nc' %grid)

# remap both land and ocean gridcells so that coastal gridcells are assigned valid values
cdo.remapnn(domain, input=crop_file, output=regrid_file)
	
# remove temp file
os.remove(crop_file)
