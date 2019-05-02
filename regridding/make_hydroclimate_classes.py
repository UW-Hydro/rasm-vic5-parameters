#!/bin/env python 

import os
import configparser
import xarray as xr
from netCDF4 import default_fillvals

# define fillvals
fillval_f = default_fillvals['f8']
fillval_i = default_fillvals['i4']

# load hydroclimate classes 
config = configparser.ConfigParser()
config.read('regridding.cfg')

# output directory for hydroclimate classes
outdir = config['Parameter Specs']['output_dir']

res = config['Parameter Specs']['res']
grid = config['Parameter Specs']['grid']

domain = xr.open_dataset(os.path.join(config['Parameter Specs']['domain_file_dir'], 
                                      config['Parameter Specs']['domain_file']))

mask_vals = domain['mask'].values

# load data used for hydroclimate classifications
# load koppen geiger 
koppen = xr.open_dataset(os.path.join(outdir, 
                                      'sdat_10012_1_20180605_141737329_%s.nc' %grid))

# Brown et al 1998 permafrost map
brown_filename = 'NCSCDv2_Circumpolar_WGS84_pfregion_extent_005deg_%s.nc' %grid
brown = xr.open_dataset(os.path.join(outdir, 
                                     brown_filename))

# make hydroclimate classes
# arid
arid = (domain.mask == 1) & (koppen.Band1 <= 8)

# temperate/dry
temp_dry = (domain.mask == 1) & (koppen.Band1 >= 8) & (koppen.Band1 <= 16)

# cold/dry with permafrost 
cold_dry_perma = ((domain.mask == 1) & (koppen.Band1 >= 17) & (koppen.Band1 <= 24) & 
                 (brown['NCSCDv2'] == 1))

# cold/dry without permafrost 
cold_dry_noperma = ((domain.mask == 1) & (koppen.Band1 >= 17) & (koppen.Band1 <= 24) & 
                 (brown['NCSCDv2'] != 1))

# Cold/WDS/WS Permafrost
cold_dry_nodry1_perma = ((domain.mask == 1) & (koppen.Band1 >= 25) 
                         & (koppen.Band1 <= 26) & (brown['NCSCDv2'] == 1))

# Cold/WDS/WS No Permafrost
cold_dry_nodry1_noperma = ((domain.mask == 1) & (koppen.Band1 >= 25) 
                         & (koppen.Band1 <= 26) & (brown['NCSCDv2'] != 1))

# Cold/WDS/cold summers Permafrost
cold_dry_nodry2_perma = ((domain.mask == 1) & (koppen.Band1 >= 27) 
                         & (koppen.Band1 <= 28) & (brown['NCSCDv2'] == 1))

# Cold/WDS/cold summers Permafrost
cold_dry_nodry2_noperma = ((domain.mask == 1) & (koppen.Band1 >= 27) 
                         & (koppen.Band1 <= 28) & (brown['NCSCDv2'] != 1))

# polar
polar = (domain.mask == 1) & (koppen.Band1 >= 29) & (koppen.Band1 <= 32)

# make NetCDF of hydroclimate classes
masks = xr.Dataset()

masks['mask_land'] = xr.DataArray(mask_vals,
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "land mask", 
                                          'units': "N/A", 'long_name': "gridcells that are land"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})

masks['arid'] = xr.DataArray(arid,
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "arid mask", 
                                          'units': "N/A", 'long_name': "arid mask"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})

masks['temperate_dry'] = xr.DataArray(temp_dry,
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "temperate/dry mask", 
                                          'units': "N/A", 'long_name': "arid mask"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})

masks['cold_dry_perma'] = xr.DataArray(cold_dry_perma,
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "cold/dry perma", 
                                          'units': "N/A", 'long_name': "cold and dry with permafrost"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})

masks['cold_dry_noperma'] = xr.DataArray(cold_dry_noperma,
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "cold/dry no perma", 
                                          'units': "N/A", 'long_name': "cold and dry no permafrost"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})

masks['cold_wds_ws_perma'] = xr.DataArray(cold_dry_nodry1_perma,
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "cold/wds/ws perma", 
                                          'units': "N/A", 'long_name': "Cold/Without Dry Season/Warm Summers with permafrost"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})

masks['cold_wds_ws_noperma'] = xr.DataArray(cold_dry_nodry1_noperma,
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "cold/wds/ws no perma", 
                                          'units': "N/A", 'long_name': "Cold/Without Dry Season/Warm Summers no permafrost"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})

masks['cold_wds_cs_perma'] = xr.DataArray(cold_dry_nodry2_perma,
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "cold/wds/cs perma", 
                                          'units': "N/A", 'long_name': "Cold/Without Dry Season/Cold Summers with permafrost"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})

masks['cold_wds_cs_noperma'] = xr.DataArray(cold_dry_nodry2_noperma,
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "cold/wds/cs no perma", 
                                          'units': "N/A", 'long_name': "Cold/Without Dry Season/Cold Summers no permafrost"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})

masks['polar'] = xr.DataArray(polar,
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "polar mask", 
                                          'units': "N/A", 'long_name': "polar"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})

# write hydroclimate classes to NetCDF file 
encoding_masks = {'mask_land': {'dtype': 'int32', "_FillValue": fillval_i},
                   'arid': {'dtype': 'int32', "_FillValue": fillval_i},
                   'temperate_dry': {'dtype': 'int32', "_FillValue": fillval_i},
                   'cold_dry_perma': {'dtype': 'int32', "_FillValue": fillval_i},
                   'cold_dry_noperma': {'dtype': 'int32', "_FillValue": fillval_i},
                   'cold_wds_ws_perma': {'dtype': 'int32', "_FillValue": fillval_i},
                   'cold_wds_ws_noperma': {'dtype': 'int32', "_FillValue": fillval_i},
                   'cold_wds_cs_perma': {'dtype': 'int32', "_FillValue": fillval_i},
                   'cold_wds_cs_noperma': {'dtype': 'int32', "_FillValue": fillval_i},
                   'polar': {'dtype': 'int32', "_FillValue": fillval_i}}
new_params_file = os.path.join(outdir, 'hydroclimate_masks_%s.nc' %grid)
masks.to_netcdf(new_params_file, format='NETCDF4_CLASSIC', encoding=encoding_masks)
