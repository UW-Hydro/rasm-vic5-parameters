# This readme contains a full description of all required data for deriving the parameters with links for downloading each dataset where available or contact information for obtaining data. 

Required data inputs and their categories: 

Soils data: obtained from the ISRIC Global 1km soils data, http://isric.org/explore/soilgrids. Links below are for the 1km product, can also use 250m if higher resolution is desired, or coarser resolution (5km, 10km, etc). 
Relevant citation: Hengl T, de Jesus JM, MacMillan RA, Batjes NH, Heuvelink GBM, et al. (2014) SoilGrids1km - Global Soil Information Based on Automated Mapping. PLoS ONE 9(8):e105992. doi:10.1371/journal.pone.0105992
	-- organic matter: ftp://ftp.soilgrids.org/data/recent/OCSTHA_M_sd1_1km.tif (download for all 7 layers, e.g. sd1-7)
	-- coarse content: ftp://ftp.soilgrids.org/data/aggregated/1km/CRFVOL_M_sl1_1km_ll.tif (download for all 7 layers, e.g. sl1-7)
	-- silt content: ftp://ftp.soilgrids.org/data/aggregated/1km/SLTPPT_M_sl1_1km_ll.tif (download for all 7 layers, e.g. sl1-7)
	-- sand content: tp://ftp.soilgrids.org/data/aggregated/1km/SNDPPT_M_sl1_1km_ll.tif (download for all 7 layers, e.g. sl1-7)
	-- clay content: ftp://ftp.soilgrids.org/data/aggregated/1km/CLYPPT_M_sl1_1km_ll.tif (download for all 7 layers, e.g. sl1-7)
	-- bulk density: ftp://ftp.soilgrids.org/data/aggregated/1km/BLDFIE_M_sl1_1km_ll.tif (download for all 7 layers, e.g. sl1-7)

LAI and Vegetation Height: 0.05-degree global product obtained from Peter Lawrence and Dave Lawrence at the Climate and Global Dynamics group, National Center for Atmospheric Research. Emails: Dave Lawrence (dlawren@ucar.edu), Peter Lawrence (lawrence@ucar.edu)

Vegetation Classes (Plant Functional Types used in CLM): same source as for LAI and Vegetation Height, 0.05-degree global product

Elevation data: 
	-- GTOPO 0.05-deg elevation map, available through Oak Ridge National Lab (required EarthData registration for download): https://webmap.ornl.gov/ogc/dataset.jsp?dg_id=10003_1

Climatological Temperature and Precipitation: 
	-- WORLDCLIM 10-min data, 1970-2000, available here: http://worldclim.org/version2

Hydroclimate classes: 
	-- Brown et al 1997 permafrost map at 0.05-degree resolution, available via the Northern Circumpolar Soil Carbon Database (NCSCD), available at multiple resolutions (highest one and the one used for this process has been the 0.05-degree product) as NetCDF files and GeoTIFF files: https://bolin.su.se/data/ncscd/netcdf.php 
	-- Koppen-Geiger global climate classes map, 0.05-degree resolution, available through Oak Ridge National Lab: https://webmap.ornl.gov/ogc/dataset.jsp?ds_id=10012

Baseflow parameters: 
	-- 1 degree global soil data, file is in this folder, titled: world.soil.parameter.txt





