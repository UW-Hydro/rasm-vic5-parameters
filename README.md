# rasm-vic5-parameters
This repo is for development of VIC 5 parameters over the RASM domain. 

Steps to derive parameters: 
1. Create domain file that is CF-compliant for desired model domain. For reference, see domain file in this folder titled: domain.lnd.wr50a_ar9v4.100920.nc 
2. Obtain required input data. See inputdata_readme.md for a full description of required input data. 
3. Regrid required data inputs after setting up regridding config file (~/regridding/regridding.cfg), 
including corresponding scripts for regridding, all located in ~/regridding: 
	-- ISRIC Soil Data: regrid_isric_soildata.py 
	-- PFTs (vegetation types): regrid_pfts.py
	-- vegetation height: regrid_veg_height.py 
	-- LAI: regrid_lai.py 
	-- precipitation and temperature: regrid_worldclim.py
	-- GTOPO elevation: regrid_gtopo.py 
	-- Koppen-Geiger hydroclimate class: regrid_koppengeiger.py 
	-- Brown permafrost data: regrid_brown_permafrost.py
	-- GMT file: regrid_off_gmt.py
4. Make hydroclimate classes using Koppen-Geiger and Brown permafrost data
	-- run ~/regridding/make_hydroclimate_classes.py 
	-- adjust paths as necessary in ~/regridding/regridding.cfg
5. Make parameter file by running ~/initial_parameters.ipynb (Jupyter notebook) 
