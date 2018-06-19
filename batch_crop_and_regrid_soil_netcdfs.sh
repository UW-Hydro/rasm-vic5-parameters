#!/bin/bash
#PBS -N regrid
#PBS -q serial
#PBS -A NPSCA07935YF5
#PBS -l select=2:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=18:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

# process soil grid NetCDFs by cropping them and then regridding them

declare -a soil_variables=("clay" "sand" "silt" "coarse" "bulk_density" "organic_fract")
###################################################################################### change domain file if needed ###########################################################
domain_file="/u/home/gergel/data/parameters/domain.lnd.wr50a_ar9v4.100920.nc"
###############################################################################################################################################################################

for soil_var in ${soil_variables[@]} 
do
	# number of soil layers in dataset (7) + 1
	nlayers=8
	
	for layer in $(seq 1 $nlayers)
	do 

		filename="/u/home/gergel/data/parameters/soil_data/netcdfs/${soil_var}_sl${layer}.nc"
		
		# crop file
		crop_file="/u/home/gergel/data/parameters/soil_data/netcdfs/cropped_${soil_var}_sl${layer}.nc"
		cdo sellonlatbox,-180,180,15,90 $filename $crop_file

		# regrid file
		tmp1="/u/home/gergel/data/parameters/soil_data/rasm_grid_netcdfs/50km/${soil_var}_sl${layer}_tmp.nc"
		tmp2="/u/home/gergel/data/parameters/soil_data/rasm_grid_netcdfs/50km/${soil_var}_sl${layer}_wr50a_ar9v4_tmp.nc"
		regrid_file="/u/home/gergel/data/parameters/soil_data/rasm_grid_netcdfs/50km/${soil_var}_sl${layer}_wr50a_ar9v4.nc"
		
		# set fillvalues to missing values to avoid incorrect remapping of coastal gridcells, 
		# solution adapted from https://code.mpimet.mpg.de/boards/2/topics/6172?r=6199
		# set valid ranges for each soil variable and remaining values to missing values
		if [ "$soil_var" == "bulk_density" ]
		then 
			# bulk density (kg/m3)
			vmin=50
			vmax=3000
		elif [ "$soil_var" == "organic_fract" ]
		then
			# soil organic carbon content (g/kg)
			vmin=0
			vmax=500
		else
			# sand, silt, coarse, clay content, volumetric (%)
			vmin=0
			vmax=100
		fi

		cdo -setvrange,$vmin,$vmax $crop_file $tmp1
		cdo setmisstonn $tmp1 $tmp2		

		# remap both land and ocean gridcells so that coastal gridcells are assigned valid values 
		# use nearest neighbor remapping for all soil variables except for organic fraction
		if [ "$soil_var" == "organic_fract" ]
		then
			cdo remapcon,$domain_file $tmp2 $regrid_file
		else
			cdo remapnn,$domain_file $tmp2 $regrid_file
		fi

		echo "successfully regridded ${file_type}_sl${layer}.nc"	
	
		# remove crop file
		rm $crop_file $tmp1 $tmp2
	done
done
