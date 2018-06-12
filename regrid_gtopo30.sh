#!/bin/bash
#PBS -N gtopo_regrid
#PBS -q serial
#PBS -A NPSCA07935YF5
#PBS -l select=2:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=12:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

# regrid GTOPO DEM to domain file listed 

###################################################################################### change domain file if needed ###########################################################
domain_file="/u/home/gergel/data/parameters/domain.lnd.wr50a_ar9v4.100920.nc"
###############################################################################################################################################################################

filename="/u/home/gergel/data/parameters/gtopo30/sdat_10003_1_20180525_151136146.nc"
		
# crop file
crop_file="/u/home/gergel/data/parameters/gtopo30/cropped_dem.nc"
cdo -sellonlatbox,-180,180,16.5,90 -selname,Band1 $filename $crop_file

# regrid file
regrid_file="/u/home/gergel/data/parameters/gtopo30/sdat_10003_1_20180525_151136146_wr50a_ar9v4.nc"
cdo remapnn,$domain_file $crop_file $regrid_file
echo "successfully regridded GTOPO30 0.05 deg Digital Elevation Map (DEM)"	
	
# remove crop file
rm $crop_file
