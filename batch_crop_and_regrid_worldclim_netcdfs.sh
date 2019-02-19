#!/bin/bash
#PBS -N worldclim
#PBS -q x11
#PBS -A NPSCA07935YF5
#PBS -l select=1:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=04:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

# process WorldClim NetCDFs by cropping them and then regridding them

declare -a clim_variables=("tavg" "prec")
#declare -a clim_variables=("tavg")

declare -a month_nums=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11" "12")

# grid options: 50km: wr50a_ar9v4, 25km: wr25b_ar9v4
grid="wr25b_ar9v4"
# res options: 50km, 25km 
res="25km"

if [ "$grid" == "wr50a_ar9v4" ]
then
        domain_file="/u/home/gergel/data/parameters/domain.lnd.wr50a_ar9v4.100920.nc"
elif [ "$grid" == "wr25b_ar9v4" ]
then
        domain_file="/u/home/gergel/data/parameters/domain.lnd.wr25b_ar9v4.170413.nc"
else
        echo "this hasn't been defined yet"
fi


for file_type in ${clim_variables[@]} 
do	
	for month_num in ${month_nums[@]} 
	do 

		filename="/u/home/gergel/data/parameters/world_clim_data/netcdfs/${file_type}_${month_num}.nc"
		
		# crop file
		crop_file="/u/home/gergel/data/parameters/world_clim_data/cropped_${file_type}_${month_num}.nc"
		cdo sellonlatbox,-180,180,15,90 $filename $crop_file

		# regrid file
		tmp1="/u/home/gergel/data/parameters/world_clim_data/${res}/${file_type}_${month_num}_tmp.nc"
		tmp2="/u/home/gergel/data/parameters/world_clim_data/${res}/${file_type}_${month_num}_${grid}_tmp.nc"
		regrid_file="/u/home/gergel/data/parameters/world_clim_data/${res}/${file_type}_${month_num}_${grid}.nc"

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
