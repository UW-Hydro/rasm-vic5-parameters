# VIC5 Parameter Development
This repo is for development of VIC 5 parameters. This python-based process is designed to be both domain and resolution agnostic, meaning the process can be applied to any resolution or domain globally. 

Steps to derive parameters: 
1. Create NetCDF domain file that is CF-compliant for desired model domain. For reference, see domain file in this folder titled: `domain.lnd.wr50a_ar9v4.100920.nc`
2. Obtain required input data. See `inputdata_readme.md` for a full description of required input data. Note that you may also adapt certain parts of the derivation process to use other base datasets if you so choose. 
3. Regrid required data inputs to desired resolution after setting up regridding config file (`~/regridding/regridding.cfg`), 
including corresponding scripts for regridding. Some base datasets will need to be converted from GeoTiffs to NetCDFs before usage, and scripts to regrid those files (the WorldClim and SoilsGrid data) are located in the home directory of this repo. Other regridding scripts are located in `~/regridding`: 
    1. ISRIC Soil Data: `regrid_isric_soildata.py`
    2. PFTs (vegetation types): `regrid_pfts.py`
    3. vegetation height: `regrid_veg_height.py`
    4. LAI: `regrid_lai.py` 
    5. precipitation and temperature: `regrid_worldclim.py`
    6. GTOPO elevation: `regrid_gtopo.py`
    7. Koppen-Geiger hydroclimate class: `regrid_koppengeiger.py` 
    8. Brown permafrost data: `regrid_brown_permafrost.py`
    9. GMT file: `regrid_off_gmt.py`
4. Make hydroclimate classes using Koppen-Geiger and Brown permafrost data
	1. run `~/regridding/make_hydroclimate_classes.py`
	2. adjust paths as necessary in `~/regridding/regridding.cfg`
5. Make parameter file by running `~/initial_parameters.ipynb` (Jupyter notebook) 

Note: this derivation process assumes that you have all of the requisite python packages installed. If you have trouble doing that, I recommend you create a virtual environment. For reference, I have included a .yml file with the requisite python packages that you may use for your python virtual environment.

If you have issues with any step of the process, please feel free to contact me at: gergel@uw.edu.
