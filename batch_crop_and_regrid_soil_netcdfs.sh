#!/bin/bash
#PBS -N regrid
#PBS -q serial
#PBS -A NPSCA07935YF5
#PBS -l select=2:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=16:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

# process soil grid NetCDFs by cropping them and then regridding them

declare -a soil_variables=("bulk_density" "clay" "sand" "silt" "coarse")
###################################################################################### change domain file if needed ###########################################################
domain_file="/u/home/gergel/data/parameters/domain.lnd.wr50a_ar9v4.100920.nc"
###############################################################################################################################################################################

for file_type in ${soil_variables[@]} 
do
	if [ "$file_type" != "bedrock" ]
	then
    		upper_range=8
	else
    		upper_range=2
	fi
	
	for layer in $(seq 1 $upper_range)
	do 

		filename="/u/home/gergel/data/parameters/soil_data/netcdfs/${file_type}_sl${layer}.nc"
		
		# crop file
		crop_file="/u/home/gergel/data/parameters/soil_data/netcdfs/cropped_${file_type}_sl${layer}.nc"
		cdo sellonlatbox,-180,180,16.5,90 $filename $crop_file

		# regrid file
		regrid_file="/u/home/gergel/data/parameters/soil_data/rasm_grid_netcdfs/${file_type}_sl${layer}.nc"
		cdo remapnn,$domain_file $crop_file $regrid_file
		echo "successfully regridded ${file_type}_sl${layer}.nc"	
	
		# remove crop file
		rm $crop_file
	done
done
