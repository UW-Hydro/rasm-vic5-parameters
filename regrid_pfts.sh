#!/bin/bash
#PBS -N pfts_regrid
#PBS -q serial
#PBS -A NPSCA07935YF5
#PBS -l select=1:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=12:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

# regrid PFTs to domain file listed 

###################################################################################### change domain file if needed ###########################################################
domain_file="/u/home/gergel/data/parameters/domain.lnd.wr50a_ar9v4.100920.nc"
###############################################################################################################################################################################

filename="/u/home/gergel/data/parameters/pfts/mksrf_landuse_rc2000_c110913_mod.nc"
		
# crop file
crop_file="/u/home/gergel/data/parameters/pfts/cropped_pfts.nc"
cdo -sellonlatbox,-180,180,16.5,90 -selname,PCT_PFT $filename $crop_file

# regrid file
regrid_file="/u/home/gergel/data/parameters/pfts/regridded_pfts/mksrf_landuse_rc2000_c110913_wr50a_ar9v4.nc"
cdo remapnn,$domain_file $crop_file $regrid_file
#cdo remapnn,$domain_file -selname,PCT_PFT $filename $regrid_file
echo "successfully regridded pfts"	
	
# remove crop file
rm $crop_file
