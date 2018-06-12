#!/bin/bash
#PBS -N worldclim
#PBS -q serial
#PBS -A NPSCA07935YF5
#PBS -l select=1:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=04:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

# process WorldClim NetCDFs by cropping them and then regridding them

#declare -a clim_variables=("tavg" "prec")
declare -a clim_variables=("tavg")

declare -a month_nums=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12")
###################################################################################### change domain file if needed ###########################################################
domain_file="/u/home/gergel/data/parameters/domain.lnd.wr50a_ar9v4.100920.nc"
###############################################################################################################################################################################

for file_type in ${clim_variables[@]} 
do	
	for month_num in ${month_nums[@]} 
	do 

		filename="/u/home/gergel/data/parameters/world_clim_data/netcdfs/${file_type}_${month_num}.nc"
		
		# crop file
		crop_file="/u/home/gergel/data/parameters/world_clim_data/cropped_${file_type}_${month_num}.nc"
		cdo sellonlatbox,-180,180,15,90 $filename $crop_file

		# regrid file
		tmp1="/u/home/gergel/data/parameters/world_clim_data/50km/${file_type}_${month_num}_tmp.nc"
		tmp2="/u/home/gergel/data/parameters/world_clim_data/50km/${file_type}_${month_num}_wr50a_ar9v4_tmp.nc"
		regrid_file="/u/home/gergel/data/parameters/world_clim_data/50km/${file_type}_${month_num}_wr50a_ar9v4.nc"

		# set fillvalues to missing values to avoid incorrect remapping of coastal gridcells, 
		# solution adapted from https://code.mpimet.mpg.de/boards/2/topics/6172?r=6199
		cdo -setvrange,-1000,1000 $crop_file $tmp1
		cdo setmisstonn $tmp1 $tmp2

		# remap both land and ocean gridcells so that coastal gridcells are assigned valid values
		cdo remapnn,$domain_file $tmp2 $regrid_file
		echo "successfully regridded ${file_type} ${month_num}"	
	
		# remove intermediate files
		rm $crop_file $tmp1 $tmp2
	done
done
