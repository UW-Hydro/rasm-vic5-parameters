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
cdo -sellonlatbox,-180,180,15,90 -selname,Band1 $filename $crop_file

# regrid file
tmp1="/u/home/gergel/data/parameters/gtopo30/sdat_10003_1_20180525_151136146_tmp.nc"
tmp2="/u/home/gergel/data/parameters/gtopo30/sdat_10003_1_20180525_151136146_wr50a_ar9v4_tmp.nc"
regrid_file="/u/home/gergel/data/parameters/gtopo30/sdat_10003_1_20180525_151136146_wr50a_ar9v4.nc"

# set fillvalues to missing values to avoid incorrect remapping of coastal gridcells, 
# solution adapted from https://code.mpimet.mpg.de/boards/2/topics/6172?r=6199
cdo -setvrange,-1000,1000 $crop_file $tmp1
cdo setmisstonn $tmp1 $tmp2

# remap both land and ocean gridcells so that coastal gridcells are assigned valid values
cdo remapnn,$domain_file $tmp2 $regrid_file
echo "successfully regridded GTOPO30 0.05 deg Digital Elevation Map (DEM)"	
	
# remove crop file
rm $crop_file $tmp1 $tmp2
