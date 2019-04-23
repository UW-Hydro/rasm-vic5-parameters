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

outdir = config['Parameter Specs']['output_dir']

filename = os.path.join(config['Hydroclimate']['dir'],
                        config['Hydroclimate']['brown_filename'])
		
# regrid file
regrid_file = os.path.join(outdir, 'NCSCDv2_Circumpolar_WGS84_pfregion_extent_005deg_%s.nc' %grid)

#cdo remapnn,$domain_file $filename $regrid_file
cdo.remapnn(domain, input=filename, output=regrid_file)
