# rasm-vic5-parameters
This repo is for development of VIC 5 parameters over the RASM domain. 

Steps to derive parameters: 
1. Create domain file that is CF-compliant for desired model domain
2. Regrid required data inputs after setting up regridding config file (~/regridding/regridding.cfg), 
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
3. Make hydroclimate classes using Koppen-Geiger and Brown permafrost data
	-- run ~/regridding/make_hydroclimate_classes.py 
	-- adjust paths as necessary in ~/regridding/regridding.cfg
4. Make parameter file by running ~/initial_parameters.ipynb (Jupyter notebook) 
