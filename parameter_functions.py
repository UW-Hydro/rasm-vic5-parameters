#!/bin/env python 

import xarray as xr
import os
import numpy as np
import matplotlib.pyplot as plt
import collections
import warnings 
from netCDF4 import default_fillvals
from scipy.stats import hmean

def is_soil_class(soil_class):
    '''
    Takes input soil classification and checks to make sure that it is greater than 0 
    (e.g. classified)
    '''
    assert soil_class > 0
        
def is_param_value(parameter):
    '''
    Takes input parameter and checks to be sure that it has been assigned a value 
    (should not be equal to 0 if it has been assigned)
    '''
    assert parameter > 0

def classify_soil_texture(sand, clay, silt):
    '''
    this function takes in percent sand and percent clay and classifies it in
    accordance with the ARS Soil Texture classes, listed here in VIC 5 Read the Docs: 
    https://vic.readthedocs.io/en/master/Documentation/soiltext/. 
    '''
    
    soil_class = 0
    
    # sand
    if silt + (1.5 * clay) < 15:
        soil_class = 1
    # loamy sand
    elif silt + (1.5 * clay) >= 15 and silt + (2 * clay) < 30:
        soil_class = 2
    # sandy loam
    elif ((clay >= 7 and clay < 20 and sand > 52 and silt + (2 * clay) >= 30) or 
          (clay < 7 and silt < 50 and silt + (2 * clay) >= 30)):
        soil_class = 3
    # loam
    elif clay >= 7 and clay < 27 and silt >= 28 and silt < 50 and sand <= 52:
        soil_class = 6
    # silt loam
    elif (silt >= 50 and clay >= 12 and clay < 27) or (silt >= 50 and silt < 80 and clay < 12):
        soil_class = 4
    # silt 
    elif silt >= 80 and clay < 12:
        soil_class = 5
    # sandy clay loam
    elif clay >= 20 and clay < 35 and silt < 28 and sand > 45:
        soil_class = 7
    # clay loam
    elif clay >= 27 and clay < 40 and sand > 20 and sand <= 45: 
        soil_class = 9
    # silty clay loam
    elif clay >= 27 and clay < 40 and sand <= 20:
        soil_class = 8
    # sandy clay 
    elif clay >= 35 and sand > 45: 
        soil_class = 10
    # silty clay
    elif clay >= 40 and silt >= 40: 
        soil_class = 11
    elif clay >= 40 and sand <= 45 and silt < 40:
        soil_class = 12
    elif np.isnan(clay):
        soil_class = 12
    
    return(soil_class)

def calculate_cv_pft(gridcell_pft):
    '''
    takes a percent PFT for a gridcell and returns the fraction of gridcell coverage for that PFT
    '''
    
    return(gridcell_pft / 100.0)

def map_pft_to_nldas_class(pft):
    '''
    this function takes in a pft and maps it to an NLDAS veg class for using NLDAS VIC 5 veg-class 
    specific parameters. 
    '''
    # bare 
    if pft == 0:
        nldas = 11
    # NET - temperate
    elif pft == 1:
        nldas = 0
    # NET - boreal
    elif pft == 2:
        nldas = 0
    # NDT - boreal
    elif pft == 3:
        nldas = 1
    # BET - tropical
    elif pft == 4:
        nldas = 2
    # BET - temperate
    elif pft == 5:
        nldas = 2
    # BDT - tropical
    elif pft == 6:
        nldas = 3
    # BDT - temperate
    elif pft == 7:
        nldas = 3
    # BDT - boreal
    elif pft == 8:
        nldas = 3
    # BES - temperate
    elif pft == 9:
        nldas = 8
    # BDS - temperate
    elif pft == 10:
        nldas = 8
    # BDS - boreal
    elif pft == 11:
        nldas = 8
    # C3 arctic grass
    elif pft == 12:
        nldas = 9
    # C3 grass
    elif pft == 13:
        nldas = 9
    # C4 grass
    elif pft == 14:
        nldas = 9
    # crops
    elif pft == 15:
        nldas = 10
    elif pft == 16: 
        nldas = 2
    else: 
        raise ValueError("this is not a PFT")
    return(nldas)

def is_overstory(nldas_class):
    '''
    function takes in an NLDAS class, if NLDAS class is 1-6 returns 1 (class has an overstory)
    if NLDAS class 7-12, return 0 (class does not have an overstory)
    '''
    if nldas <= 5:
        return(1)
    else:
        return(0)

def calc_root_fract(cv, pft, root_zone):
    # root fract is not homogenous across veg classes 
    nldas = map_pft_to_nldas_class(int(float(pft)))
    if cv > 0:
        if nldas == 0 or nldas == 1 or nldas == 2 or nldas == 3 or nldas == 4 or nldas == 5: 
            if root_zone == "1":
                root_fract = 0.3
            else: 
                root_fract = 0.7
        elif nldas == 6 or nldas == 7:
            if root_zone == "1":
                root_fract = 0.6
            else: 
                root_fract = 0.4
        elif nldas == 8 or nldas == 9 or nldas == 10: 
            if root_zone == "1":
                root_fract = 0.7
            else:
                root_fract = 0.3
        elif nldas == 11:
            if root_zone == "1":
                root_fract = 0.0
            else: 
                root_fract = 0.0
        return(root_fract)
    elif cv == 0:
        return(0)
    else:
        return(cv)

def calc_root_depth_rz1(cv):
    '''
    takes in: 
    cv: DataArray
    '''
    # root depth is homogenous across veg classes 
    # assuming root zone is 1
    if cv > 0:
        root_depth = 0.3
    else:
        root_depth = 0.0
    return(root_depth)
def calc_root_depth_rz2(cv):
    '''
    takes in: 
    cv: DataArray
    '''
    # root depth is homogenous across veg classes 
    # assuming root zone is 2
    if cv > 0:
        root_depth = 0.7
    else:
        root_depth = 0.0
    return(root_depth)

def calculate_first_layer_harmonic_mean(sl1, sl2):
    '''
    takes in two values over which to calculate the harmonic mean, uses hmean from scipy.stats package
    '''
    arr = np.array([sl1, sl2])
    return(hmean(arr))

def calculate_second_layer_harmonic_mean(sl3, sl4, sl5, sl6, sl7, total_depth):
    '''
    sl3: 0.15m, sl4: 0.3m, sl5: 0.6m, sl6: 1m, sl7: 2m
    takes in sl3-7 and returns harmonic mean of whatever layers are included in the profile
    '''
    d1 = 0.1 # spatially homogenous first layer soil depth
    d3 = 0.5 # spatially homogenous third layer soil depth
    second_layer = total_depth - (d1 + d3)
    if second_layer < 0.3:
        return(sl3)
    elif second_layer >= 0.3 and second_layer < 0.6:
        return(hmean(np.array([sl3, sl4])))
    elif second_layer >= 0.6 and second_layer <= 1:
        return(hmean(np.array([sl5, sl6])))
    elif second_layer >= 1 and second_layer <= 2:
        return(hmean(np.array([sl5, sl6])))
    elif second_layer > 2:
        return(sl6)
    else:
        raise ValueError("layer did not get assigned")

def calculate_third_layer_harmonic_mean(sl3, sl4, sl5, sl6, sl7, total_depth):
    '''
    sl3: 0.15m, sl4: 0.3m, sl5: 0.6m, sl6: 1m, sl7: 2m
    takes in sl3-7 and returns harmonic mean of whatever layers are included in the profile
    '''
    # if total_depth > 0:
    d1 = 0.1 # spatially homogenous first layer soil depth
    d3 = 0.5 # spatially homogenous third layer soil depth
    second_layer = total_depth - (d1 + d3)
    second_layer_depth = d1 + second_layer
    if second_layer_depth >= 0.1 and total_depth <= 1.0:
        return(sl4)
    elif second_layer_depth >= 0.3 and total_depth <= 1.5: 
        return(hmean(np.array([sl4, sl5, sl6])))
    elif second_layer_depth >= 0.6 and total_depth <= 1.5: 
        return(hmean(np.array([sl5, sl6])))
    elif second_layer_depth >= 1.0 and second_layer_depth < 1.5:
        return(hmean(np.array([sl6])))
    elif second_layer_depth > 1.5:
        return(sl7)
    else:
        print("second layer depth is %f " % second_layer_depth)
        print("total depth is %f" % total_depth)
        raise ValueError("layer did not get assigned")
    # else: 
        # return(0)

def calculate_first_layer_arithmetic_mean(sl1, sl2):
    '''
    takes in two values over which to calculate the arithmetic mean
    '''
    arr = np.array([sl1, sl2])
    return(np.mean(arr))

def calculate_second_layer_arithmetic_mean(sl3, sl4, sl5, sl6, sl7, total_depth):
    '''
    sl3: 0.15m, sl4: 0.3m, sl5: 0.6m, sl6: 1m, sl7: 2m
    takes in sl3-7 and returns arithmetic mean of whatever layers are included in the profile
    '''
    d1 = 0.1 # spatially homogenous first layer soil depth
    d3 = 0.5 # spatially homogenous third layer soil depth
    second_layer = total_depth - (d1 + d3)
    if second_layer < 0.3:
        return(sl3)
    elif second_layer >= 0.3 and second_layer < 0.6:
        return(np.mean(np.array([sl3, sl4])))
    elif second_layer >= 0.6 and second_layer <= 1:
        return(np.mean(np.array([sl5, sl6])))
    elif second_layer >= 1 and second_layer <= 2:
        return(np.mean(np.array([sl5, sl6])))
    elif second_layer > 2:
        return(sl6)
    else:
        raise ValueError("layer did not get assigned")

def calculate_third_layer_arithmetic_mean(sl3, sl4, sl5, sl6, sl7, total_depth):
    '''
    sl3: 0.15m, sl4: 0.3m, sl5: 0.6m, sl6: 1m, sl7: 2m
    takes in sl3-7 and returns arithmetic mean of whatever layers are included in the profile
    '''
    # if total_depth > 0:
    d1 = 0.1 # spatially homogenous first layer soil depth
    d3 = 0.5 # spatially homogenous third layer soil depth
    second_layer = total_depth - (d1 + d3)
    second_layer_depth = d1 + second_layer
    if second_layer_depth >= 0.1 and total_depth <= 1.0:
        return(sl4)
    elif second_layer_depth >= 0.3 and total_depth <= 1.5: 
        return(np.mean(np.array([sl4, sl5, sl6])))
    elif second_layer_depth >= 0.6 and total_depth <= 1.5: 
        return(np.mean(np.array([sl5, sl6])))
    elif second_layer_depth >= 1.0 and second_layer_depth < 1.5:
        return(np.mean(np.array([sl6])))
    elif second_layer_depth >= 1.5:
        return(sl7)
    else:
        raise ValueError("layer did not get assigned")
    # else: 
        # return(0)



def soil_class_values(soil_class, return_var):
    '''
    takes in a soil class (of type int) and uses lookup tables based on soil class for a number of 
    values that are either directly or indirectly used as VIC parameters. Decides which value to 
    return based on `return_var`, which is a string. 
    
    Valid values for `return_var` include: ksat, b, Wpwp_FRACT, Wcr_FRACT, resid_moist, quartz
    
    This is to get around the current issue with 
    returning multiple output arrays with xr.apply_ufunc. 
    
    Look-up values come from: 
    https://vic.readthedocs.io/en/master/Documentation/soiltext/ 
    Carsel and Parrish 1988, Table 3
    https://ral.ucar.edu/sites/default/files/public/product-tool/noah-multiparameterization-
    land-surface-model-noah-mp-lsm/soil_characteristics.html
    '''
    
    ksat = 0
    b = 0
    Wpwp_FRACT = 0
    Wcr_FRACT = 0
    resid_moist = 0
    quartz = 0
    
    # sand
    if soil_class == 1:
        ksat = 38.41
        b = 2.79
        Wpwp_FRACT = 0.033
        Wcr_FRACT = 0.091
        resid_moist = 0.02
        quartz = 0.92
        bulk_density = 1490
    # loamy sand
    elif soil_class == 2: 
        ksat = 10.87
        b = 4.26
        Wpwp_FRACT = 0.055
        Wcr_FRACT = 0.125
        resid_moist = 0.035
        quartz = 0.82
        bulk_density = 1520
    # sandy loam
    elif soil_class == 3:
        ksat = 5.24
        b = 4.74
        Wpwp_FRACT = 0.095
        Wcr_FRACT = 0.207
        resid_moist = 0.041
        quartz = 0.60
        bulk_density = 1570
    # silty loam
    elif soil_class == 4:
        ksat = 3.96
        b = 5.33
        Wpwp_FRACT = 0.133
        Wcr_FRACT = 0.33
        resid_moist = 0.015
        quartz = 0.25
        bulk_density = 1420
    # silty
    elif soil_class == 5:
        ksat = 8.59
        # NOTE: Table 3 doesn't have the class silty, using b for silty clay loam
        b = 8.72
        Wpwp_FRACT = 0.208
        Wcr_FRACT = 0.366
        resid_moist = 0.04
        quartz = 0.10
        bulk_density = 1280

    # loam
    elif soil_class == 6:
        ksat = 1.97
        b = 5.25
        Wpwp_FRACT = 0.117
        Wcr_FRACT = 0.27
        resid_moist = 0.027
        quartz = 0.40
        bulk_density = 1490
    # sandy clay loam
    elif soil_class == 7:
        ksat = 2.4
        b = 6.77
        Wpwp_FRACT = 0.148
        Wcr_FRACT = 0.255
        resid_moist = 0.068
        quartz = 0.60
        bulk_density = 1600
    # silty clay loam
    elif soil_class == 8:
        ksat = 4.57
        b = 8.72
        porosity = 0.48
        Wpwp_FRACT = 0.208
        Wcr_FRACT = 0.366
        resid_moist = 0.04
        quartz = 0.10
        bulk_density = 1380
    # clay loam
    elif soil_class == 9:
        ksat = 1.77
        b = 8.17
        porosity = 0.46
        Wpwp_FRACT = 0.197
        Wcr_FRACT = 0.318
        resid_moist = 0.075
        quartz = 0.35
        bulk_density = 1430
    # sandy clay
    elif soil_class == 10:
        ksat = 1.19
        b = 10.73
        Wpwp_FRACT = 0.239
        Wcr_FRACT = 0.339
        resid_moist = 0.109
        quartz = 0.52
        bulk_density = 1570
    # silty clay
    elif soil_class == 11:
        ksat = 2.95
        b = 10.39
        Wpwp_FRACT = 0.250
        Wcr_FRACT = 0.387
        resid_moist = 0.056
        quartz = 0.10
        bulk_density = 1350
    # clay
    elif soil_class == 12:
        ksat = 3.18
        b = 11.55
        Wpwp_FRACT = 0.272
        Wcr_FRACT = 0.396
        resid_moist = 0.09
        quartz = 0.25
        bulk_density = 1390
    elif np.isnan(soil_class):
        ksat = np.nan
        b = np.nan
        Wpwp_FRACT = np.nan
        resid_moist = np.nan
        quartz = np.nan
        bulk_density = np.nan
    else:
        ksat = 1.97
        b = 5.25
        Wpwp_FRACT = 0.117
        Wcr_FRACT = 0.27
        resid_moist = 0.027
        quartz = 0.40
        bulk_density = 1490
    if ~np.isnan(soil_class):
        # correct for units of VIC 5 parameters
        ksat = ksat * 240
        '''Wpwp_FRACT = Wpwp_FRACT / porosity 
        Wcr_FRACT = Wcr_FRACT / porosity'''

    if return_var == "ksat":
        return(ksat)
    elif return_var == "b":
        return(b)
    elif return_var == "Wpwp_FRACT":
        return(Wpwp_FRACT)
    elif return_var == "Wcr_FRACT":
        return(Wcr_FRACT)
    elif return_var == "resid_moist":
        return(resid_moist)
    elif return_var == "quartz":
        return(quartz)
    elif return_var == "bulk_density":
        return(bulk_density)

def calculate_init_moist(porosity, soil_layer_depth):
    '''
    takes in soil layer depth and porosity and calculates initial moisture, 
    makes initial moisture SATURATED
    '''
    MM_PER_M = 1000
    init_moist = porosity * soil_layer_depth * MM_PER_M

    return(init_moist)

def calculate_baseflow_parameters(domain, soil_direc, soil_filename, hydro_classes, var):
    '''
    takes in DataArrays: domain file and hydro_classes
    str: var name to return
    Returns: numpy array of var name
    '''
    import pandas as pd
    soil_file = os.path.join(soil_direc, soil_filename)

    masknan_vals = domain['mask'].where(domain['mask'] == 1).values
    names = ['runflag', 'gridcell', 'lat', 'lon', 'bi', 'd1', 'd2', 'd3', 'd4', 'N1', 'N2', 'N3', 'ksat1',
             'ksat2', 'ksat3', 'phi_s1', 'phi_s2', 'phi_s3', 'init_moist1', 'init_moist2', 'init_moist3',
             'elevation', 'depth1', 'depth2', 'depth3', 'avg_T', 'dp', 'bubble', 'quartz', 'bulk_density1',
             'bulk_density2', 'bulk_density3', 'soil_density1', 'soil_density2', 'soil_density3', 'off_gmt',
             'Wcr1', 'Wcr2', 'Wcr3', 'Wp1', 'Wp2', 'Wp3', 'surface_roughness', 'snow_roughness', 'annual_prec',
             'residual1', 'residual2', 'residual3']
    soil = pd.read_table(soil_file, delim_whitespace=True, names=names)

    d1 = np.copy(masknan_vals)
    d2 = np.copy(masknan_vals)
    d3 = np.copy(masknan_vals)
    d4 = np.copy(masknan_vals)

    # arid
    gc = soil.loc[(soil['lat'] > 38) & (soil['lat'] < 40) & (soil['lon'] < 107) & (soil['lon'] > 104)]
    d1[np.nonzero(hydro_classes['arid'].values)] = gc['d1'].values[0]
    d2[np.nonzero(hydro_classes['arid'].values)] = gc['d2'].values[0]
    d3[np.nonzero(hydro_classes['arid'].values)] = gc['d3'].values[0]
    d4[np.nonzero(hydro_classes['arid'].values)] = gc['d4'].values[0]

    # temperate dry 
    gc = soil.loc[(soil['lat'] > 30) & (soil['lat'] < 32) & (soil['lon'] < 116) & (soil['lon'] > 114)]
    d1[np.nonzero(hydro_classes['temperate_dry'].values)] = gc['d1'].values[0]
    d2[np.nonzero(hydro_classes['temperate_dry'].values)] = gc['d2'].values[0]
    d3[np.nonzero(hydro_classes['temperate_dry'].values)] = gc['d3'].values[0]
    d4[np.nonzero(hydro_classes['temperate_dry'].values)] = gc['d4'].values[0]

    # cold_dry_perma
    gc = soil.loc[(soil['lat'] > 55) & (soil['lat'] < 59) & (soil['lon'] < 118) & (soil['lon'] > 115)]
    d1[np.nonzero(hydro_classes['cold_dry_perma'].values)] = gc['d1'].values[0]
    d2[np.nonzero(hydro_classes['cold_dry_perma'].values)] = gc['d2'].values[0]
    d3[np.nonzero(hydro_classes['cold_dry_perma'].values)] = gc['d3'].values[0]
    d4[np.nonzero(hydro_classes['cold_dry_perma'].values)] = gc['d4'].values[0]

    # cold_dry_noperma
    gc = soil.loc[(soil['lat'] > 59) & (soil['lat'] < 62) & (soil['lon'] < 144) & (soil['lon'] > 141)]
    d1[np.nonzero(hydro_classes['cold_dry_noperma'].values)] = gc['d1'].values[0]
    d2[np.nonzero(hydro_classes['cold_dry_noperma'].values)] = gc['d2'].values[0]
    d3[np.nonzero(hydro_classes['cold_dry_noperma'].values)] = gc['d3'].values[0]
    d4[np.nonzero(hydro_classes['cold_dry_noperma'].values)] = gc['d4'].values[0]

    # cold_wds_ws_perma
    gc = soil.loc[(soil['lat'] > 46) & (soil['lat'] < 49) & (soil['lon'] < -117) & (soil['lon'] > -120)]
    d1[np.nonzero(hydro_classes['cold_wds_ws_perma'].values)] = gc['d1'].values[0]
    d2[np.nonzero(hydro_classes['cold_wds_ws_perma'].values)] = gc['d2'].values[0]
    d3[np.nonzero(hydro_classes['cold_wds_ws_perma'].values)] = gc['d3'].values[0]
    d4[np.nonzero(hydro_classes['cold_wds_ws_perma'].values)] = gc['d4'].values[0]

    # cold_wds_ws_noperma
    gc = soil.loc[(soil['lat'] > 52) & (soil['lat'] < 54) & (soil['lon'] < 36) & (soil['lon'] > 34)]
    d1[np.nonzero(hydro_classes['cold_wds_ws_noperma'].values)] = gc['d1'].values[0]
    d2[np.nonzero(hydro_classes['cold_wds_ws_noperma'].values)] = gc['d2'].values[0]
    d3[np.nonzero(hydro_classes['cold_wds_ws_noperma'].values)] = gc['d3'].values[0]
    d4[np.nonzero(hydro_classes['cold_wds_ws_noperma'].values)] = gc['d4'].values[0]

    # cold_wds_cs_perma
    gc = soil.loc[(soil['lat'] > 63) & (soil['lat'] < 66) & (soil['lon'] < 162) & (soil['lon'] > 159)]
    d1[np.nonzero(hydro_classes['cold_wds_cs_perma'].values)] = gc['d1'].values[0]
    d2[np.nonzero(hydro_classes['cold_wds_cs_perma'].values)] = gc['d2'].values[0]
    d3[np.nonzero(hydro_classes['cold_wds_cs_perma'].values)] = gc['d3'].values[0]
    d4[np.nonzero(hydro_classes['cold_wds_cs_perma'].values)] = gc['d4'].values[0]

    # cold_wds_cs_noperma
    gc = soil.loc[(soil['lat'] > 60) & (soil['lat'] < 63) & (soil['lon'] < 24) & (soil['lon'] > 22)]
    d1[np.nonzero(hydro_classes['cold_wds_cs_noperma'].values)] = gc['d1'].values[0]
    d2[np.nonzero(hydro_classes['cold_wds_cs_noperma'].values)] = gc['d2'].values[0]
    d3[np.nonzero(hydro_classes['cold_wds_cs_noperma'].values)] = gc['d3'].values[0]
    d4[np.nonzero(hydro_classes['cold_wds_cs_noperma'].values)] = gc['d4'].values[0]

    # polar
    gc = soil.loc[(soil['lat'] > 68) & (soil['lat'] < 71) & (soil['lon'] < -69) & (soil['lon'] > -73)]
    d1[np.nonzero(hydro_classes['polar'].values)] = gc['d1'].values[0]
    d2[np.nonzero(hydro_classes['polar'].values)] = gc['d2'].values[0]
    d3[np.nonzero(hydro_classes['polar'].values)] = gc['d3'].values[0]
    d4[np.nonzero(hydro_classes['polar'].values)] = gc['d4'].values[0]

    if var == "d1":
        return(d1)
    elif var == "d2":
        return(d2)
    elif var == "d3":
        return(d3)
    elif var == "d4":
        return(d4)

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

def calculate_nveg_pfts(gridcell_pfts):
    '''
    takes in the 17 PFTs for a gridcell and returns the number of active veg types for that gridcell,
    e.g. the number of PCT_PFTs that is greater than 0
    '''
    active_pfts = np.count_nonzero(gridcell_pfts[1:])
    if gridcell_pfts[0] == 100 and active_pfts == 0:
        # this is a pure bare soil gridcell
        return(0)
    elif gridcell_pfts[0] == 100 and active_pfts > 0:
        # this is a bare soil gridcell but has a nonzero fraction active 
        # of another veg type 
        # this is essentially the rounding error case
        return(active_pfts)
    else:
        # not bare soil
        active_pfts = np.count_nonzero(gridcell_pfts[1:])
        return(active_pfts)

def create_parameter_dataset(domain, old_params, nj, ni, num_veg,
                             organic_fract, max_snow_albedo,
                             bulk_density_comb):
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
   params['nlayer'] = xr.DataArray(np.arange(0, 3), dims='nlayer')

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
   params['elev'] = xr.DataArray(np.copy(masknan_vals),
                                dims=('nj', 'ni'),
                                coords={'xc': domain.xc, 'yc': domain.yc},
                                attrs={'description': "Average elevation of grid cell",
                                              'units': "m", 'long_name': "elev"},
                                encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['avg_T'] = xr.DataArray(np.copy(masknan_vals),
                                dims=('nj', 'ni'),
                                coords={'xc': domain.xc, 'yc': domain.yc},
                                attrs={'description': "Average soil temperature, used as the bottom boundary \
                                        for soil heat flux solutions",
                                        'units': "C", 'long_name': "avg_T"},
                                encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['annual_prec'] = xr.DataArray(np.copy(masknan_vals),
                                dims=('nj', 'ni'),
                                coords={'xc': domain.xc, 'yc': domain.yc},
                                attrs={'description': "Average annual precipitation",
                                              'units': "mm", 'long_name': "annual_prec"},
                                encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['rough'] = xr.DataArray(np.copy(masknan_vals),
                                dims=('nj', 'ni'),
                                coords={'xc': domain.xc, 'yc': domain.yc},
                                attrs={'description': "Surface roughness of bare soil",
                                              'units': "m", 'long_name': "rough"},
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
   params['Ds'] = xr.DataArray(np.copy(masknan_vals),
                              dims=('nj', 'ni'),
                              coords={'xc': domain.xc, 'yc': domain.yc},
                              attrs={'description': "Fraction of Dsmax where non-linear baseflow begins",
                                         'units': "fraction", 'long_name': "Ds"},
                                 encoding={"_FillValue": fillval_f,
                                           "Coordinates": "xc yc"})
   params['Dsmax'] = xr.DataArray(np.copy(masknan_vals),
                              dims=('nj', 'ni'),
                              coords={'xc': domain.xc, 'yc': domain.yc},
                              attrs={'description': "Fraction of maximum soil moisture where non-linear baseflow occurs",
                                              'units': "fraction", 'long_name': "Dsmax"},
                                 encoding={"_FillValue": fillval_f,
                                           "Coordinates": "xc yc"})
   params['Ws'] = xr.DataArray(np.copy(masknan_vals),
                              dims=('nj', 'ni'),
                              coords={'xc': domain.xc, 'yc': domain.yc},
                              attrs={'description': "Fraction of maximum soil moisture where non-linear baseflow occurs",
                                              'units': "fraction", 'long_name': "Ws"},
                                 encoding={"_FillValue": fillval_f,
                                           "Coordinates": "xc yc"})
   params['c'] = xr.DataArray(np.copy(masknan_vals),
                           dims=('nj', 'ni'),
                           coords={'xc': domain.xc, 'yc': domain.yc},
                           attrs={'description': "Exponent used in baseflow curve, normally set to 2",
                                      'units': "N/A", 'long_name': "c"},
                           encoding={"_FillValue": fillval_f,
                                  "Coordinates": "xc yc"})
   params['infilt'] = xr.DataArray(np.copy(masknan_vals),
                              dims=('nj', 'ni'),
                              coords={'xc': domain.xc, 'yc': domain.yc},
                              attrs={'description': "Fraction of maximum soil moisture where non-linear baseflow occurs",
                                              'units': "fraction", 'long_name': "infilt"},
                                 encoding={"_FillValue": fillval_f,
                                           "Coordinates": "xc yc"})
   params['depth'] = xr.DataArray(np.copy(arr_nlayer),
                                dims=('nlayer','nj', 'ni'),
                                coords={'xc': domain.xc, 'yc': domain.yc},
                                attrs={'description': "Thickness of each soil moisture layer",
                                   'units': "m", 'long_name': "depth"},
                                encoding={"_FillValue": fillval_f,
                                       "Coordinates": "xc yc"})
   params['Ksat'] = xr.DataArray(np.copy(arr_nlayer),
                              dims=('nlayer','nj', 'ni'),
                              coords={'xc': domain.xc, 'yc': domain.yc},
                              attrs={'description': "Saturated hydraulic conductivity",
                                       'units': "mm/day", 'long_name': "Ksat"},
                              encoding={"_FillValue": fillval_f,
                                         "Coordinates": "xc yc"})
   params['bulk_density'] = xr.DataArray(np.copy(arr_nlayer),
                                      dims=('nlayer','nj', 'ni'),
                                      coords={'xc': domain.xc, 'yc': domain.yc},
                                      attrs={'description': "Mineral bulk density of soil layer",
                                             'units': "kg/m3", 'long_name': "bulk_density"},
                                      encoding={"_FillValue": fillval_f,
                                             "Coordinates": "xc yc"})
   params['expt'] = xr.DataArray(np.copy(arr_nlayer),
                                   dims=('nlayer','nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "Exponent n (=3+2/lambda) in Campbell's eqt for Ksat, HBH 5.6 \
                                           where lambda = soil pore size distribution parameter",
                                           'units': "N/A", 'long_name': "expt"},
                                   encoding={"_FillValue": fillval_f,
                                             "Coordinates": "xc yc"})
   params['bubble'] = xr.DataArray(np.copy(arr_nlayer),
                                         dims=('nlayer','nj', 'ni'),
                                         coords={'xc': domain.xc, 'yc': domain.yc},
                                         attrs={'description': "Bubbling pressure of soil. Values should be > 0",
                                           'units': "cm", 'long_name': "bubble"},
                                     encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['resid_moist'] = xr.DataArray(np.copy(arr_nlayer),
                                         dims=('nlayer','nj', 'ni'),
                                         coords={'xc': domain.xc, 'yc': domain.yc},
                                         attrs={'description': "Soil moisture layer residual moisture",
                                           'units': "fraction", 'long_name': "resid_moist"},
                                         encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['quartz'] = xr.DataArray(np.copy(arr_nlayer),
                                dims=('nlayer','nj', 'ni'),
                                coords={'xc': domain.xc, 'yc': domain.yc},
                                attrs={'description': "Quartz content of soil",
                                       'units': "cm", 'long_name': "quartz"},
                                encoding={"_FillValue": fillval_f,
                                       "Coordinates": "xc yc"})
   if bulk_density_comb == True:
      params['bulk_density_comb'] = xr.DataArray(np.copy(arr_nlayer),
                                      dims=('nlayer','nj', 'ni'),
                                      coords={'xc': domain.xc, 'yc': domain.yc},
                                      attrs={'description': "Soil bulk density of soil layer",
                                             'units': "kg/m3", 'long_name': "bulk_density"},
                                      encoding={"_FillValue": fillval_f,
                                             "Coordinates": "xc yc"})
   if organic_fract == True:
      params['organic'] = xr.DataArray(np.copy(arr_nlayer),
                                      dims=('nlayer','nj', 'ni'),
                                      coords={'xc': domain.xc, 'yc': domain.yc},
                                      attrs={'description': "soil organic carbon fraction",
                                             'units': "fraction", 'long_name': "organic_fract"},
                                      encoding={"_FillValue": fillval_f,
                                             "Coordinates": "xc yc"})
   params['soil_density'] = xr.DataArray(np.copy(arr_nlayer),
                                      dims=('nlayer','nj', 'ni'),
                                      coords={'xc': domain.xc, 'yc': domain.yc},
                                      attrs={'description': "Soil particle density, normally 2685 kg/m3",
                                       'units': "kg/m3", 'long_name': "soil_density"},
                                      encoding={"_FillValue": fillval_f,
                                           "Coordinates": "xc yc"})
   if organic_fract == True:
      params['soil_density_org'] = xr.DataArray(np.copy(arr_nlayer),
                                      dims=('nlayer','nj', 'ni'),
                                      coords={'xc': domain.xc, 'yc': domain.yc},
                                      attrs={'description': "Organic matter particle density, normally 1300 kg/m3",
                                       'units': "kg/m3", 'long_name': "soil_dens_org"},
                                      encoding={"_FillValue": fillval_f,
                                           "Coordinates": "xc yc"})
   params['Wpwp_FRACT'] = xr.DataArray(np.copy(arr_nlayer),
                                         dims=('nlayer','nj', 'ni'),
                                         coords={'xc': domain.xc, 'yc': domain.yc},
                                         attrs={'description': "Fractional soil moisture content at the \
                                                wilting point (fraction of maximum moisture)",
                                           'units': "fraction", 'long_name': "Wpwp_FRACT"},
                                         encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['Wcr_FRACT'] = xr.DataArray(np.copy(arr_nlayer),
                                         dims=('nlayer','nj', 'ni'),
                                         coords={'xc': domain.xc, 'yc': domain.yc},
                                         attrs={'description': "Fractional soil moisture content at the critical point \
                                                (~70%% of field capacity) (fraction of maximum moisture)",
                                           'units': "fraction", 'long_name': "Wcr_FRACT"},
                                         encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['init_moist'] = xr.DataArray(np.copy(arr_nlayer),
                                     dims=('nlayer','nj', 'ni'),
                                     coords={'xc': domain.xc, 'yc': domain.yc},
                                     attrs={'description': "Initial layer moisture content",
                                           'units': "mm", 'long_name': "init_moist"},
                                     encoding={"_FillValue": fillval_f,
                                             "Coordinates": "xc yc"})
   params['off_gmt'] = xr.DataArray(np.copy(masknan_vals),
                                 dims=('nj', 'ni'),
                                 coords={'xc': domain.xc, 'yc': domain.yc},
                                 encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['phi_s'] = xr.DataArray(np.copy(arr_nlayer),
                                    dims=('nlayer','nj', 'ni'),
                                    coords={'xc': domain.xc, 'yc': domain.yc},
                                    attrs={'description': "Soil moisture diffusion parameter",
                                           'units': "mm/mm", 'long_name': "phi_s"},
                                    encoding={"_FillValue": fillval_f,
                                              "Coordinates": "xc yc"})
   params['fs_active'] = xr.DataArray(np.copy(masknan_vals),
                                dims=('nj', 'ni'),
                                coords={'xc': domain.xc, 'yc': domain.yc},
                                attrs={'description': "If set to 1, then frozen soil algorithm is activated for the \
                                        grid cell. A 0 indicates that frozen soils are not computed if soil \
                                        temperatures fall below 0C.",
                                        'units': "binary", 'long_name': "fs_active"},
                                encoding={"_FillValue": fillval_i,
                                               "Coordinates": "xc yc", 'dtype': 'int32'})
   params['dp'] = xr.DataArray(np.copy(masknan_vals),
                                dims=('nj', 'ni'),
                                coords={'xc': domain.xc, 'yc': domain.yc},
                                attrs={'description': "Soil thermal damping depth (depth at which soil temperature) \
                                        remains constant through the year, ~4 m",
                                              'units': "m", 'long_name': "dp"},
                                encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['snow_rough'] = xr.DataArray(np.copy(masknan_vals),
                                    dims=('nj', 'ni'),
                                    coords={'xc': domain.xc, 'yc': domain.yc},
                                    attrs={'description': "Surface roughness of snowpack",
                                              'units': "m", 'long_name': "snow_rough"},
                                    encoding={"_FillValue": fillval_f,
                                               "Coordinates": "xc yc"})
   params['run_cell'] = xr.DataArray(np.copy(masknan_vals),
                                       dims=('nj', 'ni'),
                                       coords={'xc': domain.xc, 'yc': domain.yc},
                                       attrs={'units': "N/A", 'long_name': "run_cell"},
                                       encoding={"_FillValue": fillval_i,
                                                 "Coordinates": "xc yc",
                                                 "dtype": "int32"})
   params['mask'] = xr.DataArray(np.copy(masknan_vals),
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "0 value indicates cell is not active",
                                          'units': "N/A", 'long_name': "mask", 'bounds': 'yv'},
                                   encoding={"_FillValue": fillval_i,
                                                 "Coordinates": "xc yc",
                                                 "dtype": "int32"})
   params['gridcell'] = xr.DataArray(np.copy(masknan_vals),
                                       dims=('nj', 'ni'),
                                       coords={'xc': domain.xc, 'yc': domain.yc},
                                       attrs={'description': "Grid cell number",
                                              'units': "N/A", 'long_name': "gridcell"},
                                       encoding={"_FillValue": fillval_i,
                                                 "Coordinates": "xc yc", "dtype": "int32"})
   params['lats'] = xr.DataArray(np.copy(masknan_vals),
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "Latitude of grid cell",
                                              'units': "degrees", 'long_name': "lats"})
   params['lons'] = xr.DataArray(np.copy(masknan_vals),
                                   dims=('nj', 'ni'),
                                   coords={'xc': domain.xc, 'yc': domain.yc},
                                   attrs={'description': "Longitude of grid cell",
                                          'units': "degrees", 'long_name': "lons"})
   params['xc'] = xr.DataArray(np.copy(masknan_vals),
                                 dims=('nj', 'ni'),
                                 attrs={'units': "degrees_east", 'long_name': "longitude of gridcell center",
                                        'bounds': 'xv'})
   params['yc'] = xr.DataArray(np.copy(masknan_vals),
                                 dims=('nj', 'ni'),
                                 attrs={'units': "degrees_north", 'long_name': "latitude of gridcell center",
                                        'bounds': 'yv'})
   domain = domain.rename({'nv': 'nv4'})
   params['xv'] = xr.DataArray(np.rollaxis(domain['xv'].values, axis=2),
                                 dims=('nv4', 'nj', 'ni'),
                                 attrs={'units': "degrees_east",
                                        'long_name': "longitude of grid cell vertices"})
   params['yv'] = xr.DataArray(np.rollaxis(domain['yv'].values, axis=2),
                                 dims=('nv4', 'nj', 'ni'),
                                 attrs={'units': "degrees_north",
                                        'long_name': "latitude of grid cell vertices"})
   return(params)

