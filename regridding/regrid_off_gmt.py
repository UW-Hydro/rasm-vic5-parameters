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

filename="/u/home/gergel/data/vic_params_wr50a_vic5.0.dev_20160328.nc"

filename = os.path.join(config['Other']['dir'],
                        config['Other']['off_gmt_filename'])

crop_file = os.path.join(outdir, 'cropped_off_gmt.nc')
cdo.selname('off_gmt', input=filename, output=crop_file)

tmp1 = os.path.join(outdir, 'off_gmt_tmp1_%s.nc' %grid)
tmp2 = os.path.join(outdir, 'off_gmt_tmp2_%s.nc' %grid)
regrid_file = os.path.join(outdir, 'off_gmt_%s.nc' %grid)

# set fillvalues to missing values to avoid incorrect remapping of coastal gridcells, 
# solution adapted from https://code.mpimet.mpg.de/boards/2/topics/6172?r=6199
cdo.setvrange('-43198560000000,43199280000000', input=crop_file, output=tmp1)
cdo.setmisstonn(input=tmp1, output=tmp2)

# remap both land and ocean gridcells so that coastal gridcells are assigned valid values
# cdo remapnn,$domain_file $tmp2 $regrid_file
cdo.remapnn(domain, input=tmp2, output=tmp2)
echo "successfully regridded off_gmt from 50km parameter file"     

# remove temp files
rm_files = [crop_file, tmp1, tmp2]
for file_obj in rm_files:
        os.remove(file_obj)
