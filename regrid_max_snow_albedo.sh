#!/bin/bash
#PBS -N albedo_25km
#PBS -q vnc
#PBS -A NPSCA07935YF5
#PBS -l select=1:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=18:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

# regrid PFTs to domain file listed 

# grid options: 50km: wr50a_ar9v4, 25km: wr25b_ar9v4
grid="wr25b_ar9v4"

if [ "$grid" == "wr50a_ar9v4" ]
then
        domain_file="/u/home/gergel/data/parameters/domain.lnd.wr50a_ar9v4.100920.nc"
	res="50km"
elif [ "$grid" == "wr25b_ar9v4" ]
then
        domain_file="/u/home/gergel/data/parameters/domain.lnd.wr25b_ar9v4.170413.nc"
	res="25km"
else
        echo "this hasn't been defined yet"
fi

echo "grid is ${grid}"
echo "using $domain_file for regridding"

filename="/u/home/gergel/data/parameters/max_snow_albedo/max_snow_albedo_barlage_global.nc"
		
# crop file
crop_file="/u/home/gergel/data/parameters/pfts/cropped_max_snow_albedo_${grid}.nc"
cdo -sellonlatbox,-180,180,15,90 -selname,max_snow_albedo $filename $crop_file

# regrid file
tmp1="/u/home/gergel/data/parameters/max_snow_albedo/regridded_max_snow_albedo/maxsnowalbedo_tmp_${grid}.nc"
tmp2="/u/home/gergel/data/parameters/max_snow_albedo/regridded_max_snow_albedo/maxsnowalbedo_${grid}_tmp.nc"
regrid_file="/u/home/gergel/data/parameters/max_snow_albedo/regridded_max_snow_albedo/barlage_maximum_snow_albedo_${grid}.nc"

# set fillvalues to missing values to avoid incorrect remapping of coastal gridcells, 
# solution adapted from https://code.mpimet.mpg.de/boards/2/topics/6172?r=6199
cdo -setvrange,0.0,1.0 $crop_file $tmp1
cdo setmisstonn $tmp1 $tmp2

# remap both land and ocean gridcells so that coastal gridcells are assigned valid values
cdo remapnn,$domain_file $tmp2 $regrid_file
echo "successfully regridded pfts"	
	
# remove crop file
rm $crop_file $tmp1 $tmp2
