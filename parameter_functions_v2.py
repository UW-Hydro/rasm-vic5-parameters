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

def calculate_cv_pft(gridcell_pft):
    '''
    takes a percent PFT for a gridcell and returns the fraction of gridcell coverage for that PFT
    '''
    
    return(gridcell_pft / 100.0)

def calculate_nveg_pfts(gridcell_pfts):
    '''
    takes in the 17 PFTs for a gridcell and returns the number of active veg types for that gridcell,
    e.g. the number of PCT_PFTs that is greater than 0
    '''
    return(np.count_nonzero(gridcell_pfts))

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

def calculate_init_moist(porosity, soil_layer_depth):
    '''
    takes in soil layer depth and porosity and calculates initial moisture, 
    makes initial moisture SATURATED
    '''
    MM_PER_M = 1000
    init_moist = porosity * soil_layer_depth * MM_PER_M
    
    return(init_moist)
