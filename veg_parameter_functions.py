#!/bin/env python 

import xarray as xr
import os
import numpy as np
import matplotlib.pyplot as plt
import collections
import warnings
import pandas as pd
from netCDF4 import default_fillvals
from scipy.stats import hmean

def create_empty_arrays(domain, nj, ni, num_veg):
   '''
   takes in DataSet of domain file, scalars for nj and ni 
   (size of array)
   '''
   masknan_vals = domain['mask'].where(domain['mask'] == 1).values

   arr_months = np.rollaxis(np.dstack((masknan_vals, masknan_vals, masknan_vals, masknan_vals,
                                    masknan_vals, masknan_vals, masknan_vals, masknan_vals,
                                    masknan_vals, masknan_vals, masknan_vals, masknan_vals)),
                        axis=2)
   arr_nlayer = np.rollaxis(np.dstack((masknan_vals, masknan_vals, masknan_vals)),
                        axis=2)

   arr_rootzone = np.rollaxis(np.dstack((masknan_vals, masknan_vals)),
                        axis=2)

   arr_veg_classes = np.rollaxis(np.dstack((masknan_vals, masknan_vals, masknan_vals, masknan_vals,
                                         masknan_vals, masknan_vals, masknan_vals, masknan_vals,
                                         masknan_vals, masknan_vals, masknan_vals, masknan_vals,
                                         masknan_vals, masknan_vals, masknan_vals, masknan_vals,
                                         masknan_vals)),
                              axis=2)
   arr_veg_classes_rootzone = np.vstack((arr_rootzone, arr_rootzone, arr_rootzone, arr_rootzone,
                                      arr_rootzone, arr_rootzone, arr_rootzone, arr_rootzone,
                                      arr_rootzone, arr_rootzone, arr_rootzone, arr_rootzone,
                                      arr_rootzone, arr_rootzone, arr_rootzone,
                                      arr_rootzone, arr_rootzone)).reshape(num_veg, 2, nj, ni)
   arr_veg_classes_month = np.vstack((arr_months, arr_months, arr_months, arr_months, arr_months,
                                   arr_months, arr_months, arr_months, arr_months, arr_months,
                                   arr_months, arr_months, arr_months, arr_months, arr_months,
                                   arr_months, arr_months,)).reshape(num_veg, 12, nj, ni)
   return(arr_months, arr_nlayer, arr_rootzone, arr_veg_classes, arr_veg_classes_rootzone,
          arr_veg_classes_month)


def create_veg_parameter_dataset(domain, old_params, nj, ni, num_veg,
                                 max_snow_albedo):
   '''
   takes in: 
   returns parameter DataSet
   '''
   from netCDF4 import default_fillvals
   # define fillvals
   fillval_f = default_fillvals['f8']
   fillval_i = default_fillvals['i4']

   masknan_vals = domain['mask'].where(domain['mask'] == 1).values

   arr_months, arr_nlayer, \
   arr_rootzone, arr_veg_classes, \
   arr_veg_classes_rootzone, \
   arr_veg_classes_month = create_empty_arrays(domain, nj, ni, num_veg)

   params = xr.Dataset()

   # assign veg class indexing
   params['veg_class'] = xr.DataArray(np.arange(1, 18), dims='veg_class',
                                   attrs={'long_name': "vegetation class"})

   params['Cv'] = xr.DataArray(np.copy(arr_veg_classes),
                                 dims=('veg_class','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 attrs={'description': "Fraction of grid cell covered by vegetation tile",
                                        'units': "fraction", 'long_name': "Cv"},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['Nveg'] = xr.DataArray(np.copy(masknan_vals),
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "Number of vegetation tiles in the grid cell",
                                          'units': "N/A", 'long_name': "Nveg"},
                                   encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})
   params['trunk_ratio'] = xr.DataArray(arr_veg_classes,
                                 dims=('veg_class','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 attrs={'description': "Ratio of total tree height that is trunk \
                                 (no branches) \
                                        The default value has been 0.2",
                                 'units': "fraction", 'long_name': "Cv"},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['rarc'] = xr.DataArray(arr_veg_classes,
                                 dims=('veg_class','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 attrs={'description': "Architectural resistance of vegetation type \(~2 s/m)",
                                        'units': "s/m", 'long_name': "rarc"},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['rmin'] = xr.DataArray(np.copy(arr_veg_classes),
                                 dims=('veg_class','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 attrs={'description': "Minimum stomatal resistance of vegetation type (~100 s/m)"},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['wind_h'] = xr.DataArray(np.copy(arr_veg_classes),
                                 dims=('veg_class','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 attrs={'description': "Height at which wind speed is measured",
                                        'units': "m", 'long_name': "wind_h"},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})

   params['RGL'] = xr.DataArray(np.copy(arr_veg_classes),
                                 dims=('veg_class','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 attrs={'description': "Minimum incoming shortwave radiation at which there will be \
                                        transpiration. For trees this is about 30 W/m^2, for crops about 100 W/m^2",
                                        'units': "W/m^2", 'long_name': "RGL"},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})

   params['rad_atten'] = xr.DataArray(arr_veg_classes,
                                 dims=('veg_class','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 attrs={'description': "Radiation attenuation factor. Normally set to 0.5, though may \
                                        need to be adjusted for high latitudes",
                                        'units': "fraction", 'long_name': "rad_atten"},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})

   params['wind_atten'] = xr.DataArray(arr_veg_classes,
                                 dims=('veg_class','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 attrs={'description': "Wind speed attenuation through the overstory. The default value \
                                        has been 0.5",
                                        'units': "fraction", 'long_name': "wind_atten"},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   if max_snow_albedo == True:
       params['max_snow_albedo'] = xr.DataArray(np.copy(arr_veg_classes),
                                 dims=('veg_class','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 attrs={'description': "maximum snow albedo from Barlage et al 2005",
                                        'units': "fraction", 'long_name': "max_snow_albedo"},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['albedo'] = xr.DataArray(arr_veg_classes_month,
                                         dims=('veg_class','month','nj', 'ni'),
                                         coords={'xc': domain.xc, 'yc': domain.yc},
                                         attrs={'description': "Shortwave albedo for vegetation type",
                                                'units': "fraction", 'long_name': "albedo"},
                                         encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})

   params['LAI'] = xr.DataArray(np.copy(arr_veg_classes_month),
                                 dims=('veg_class','month','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc, 'month': old_params.month},
                                 attrs={'description': "Leaf Area Index, one per month",
                                        'units': "N/A", 'long_name': "LAI"},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['overstory'] = xr.DataArray(arr_veg_classes,
                                 dims=('veg_class','nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 attrs={'description': "Flag to indicate whether or not the current vegetation type \
                                        has an overstory (TRUE for overstory present (e.g. trees), FALSE for \
                                        overstory not present (e.g. grass))",
                                        'units': "N/A", 'long_name': "overstory"},
                                 encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})
   params['displacement'] = xr.DataArray(np.copy(arr_veg_classes_month),
                                         dims=('veg_class','month','nj', 'ni'),
                                         coords={'month': old_params['month'], 'xc': domain.xc,
                                                 'yc': domain.yc},
                                         attrs={'description': "Vegetation displacement height (typically 0.67 \
                                                * vegetation height)",
                                                'units': "m", 'long_name': "displacement"},
                                         encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['veg_rough'] = xr.DataArray(np.copy(arr_veg_classes_month),
                                         dims=('veg_class','month','nj', 'ni'),
                                         coords={'xc': domain.xc, 'yc': domain.yc},
                                         attrs={'description': "Vegetation roughness length (typically 0.123 \
                                                * vegetation height)",
                                                'units': "m", 'long_name': "veg_rough"},
                                         encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['root_depth'] = xr.DataArray(np.copy(arr_veg_classes_rootzone),
                                         dims=('veg_class','root_zone','nj', 'ni'),
                                         coords={'xc': domain.xc, 'yc': domain.yc},
                                         attrs={'description': "Root zone thickness (sum of depths is total depth of \
                                                 root penetration)",
                                                'units': "m", 'long_name': "root_depth"},
                                         encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['root_fract'] = xr.DataArray(np.copy(arr_veg_classes_rootzone),
                                         dims=('veg_class','root_zone','nj', 'ni'),
                                         coords={'xc': domain.xc, 'yc': domain.yc},
                                         attrs={'description': "Fraction of root in the current root zone",
                                                'units': "fraction", 'long_name': "root_fract"},
                                         encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   return(params)
