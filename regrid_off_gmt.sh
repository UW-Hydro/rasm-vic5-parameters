#!/bin/bash
#PBS -N offgmt
#PBS -q x11
#PBS -A NPSCA07935YF5
#PBS -l select=1:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=12:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

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

echo "grid is ${grid}"
echo "using $domain_file for regridding"

filename="/u/home/gergel/data/vic_params_wr50a_vic5.0.dev_20160328.nc"

crop_file="/u/home/gergel/data/parameters/pfts/cropped_off_gmt.nc"
cdo -selname,off_gmt $filename $crop_file

# regrid file
tmp1="/u/home/gergel/data/parameters/off_gmt_tmp1_${grid}.nc"
tmp2="/u/home/gergel/data/parameters/off_gmt_tmp2_${grid}.nc"
regrid_file="/u/home/gergel/data/parameters/off_gmt_${grid}.nc"

# set fillvalues to missing values to avoid incorrect remapping of coastal gridcells, 
# solution adapted from https://code.mpimet.mpg.de/boards/2/topics/6172?r=6199
cdo -setvrange,-43198560000000,43199280000000 $crop_file $tmp1
cdo setmisstonn $tmp1 $tmp2

# remap both land and ocean gridcells so that coastal gridcells are assigned valid values
cdo remapnn,$domain_file $tmp2 $regrid_file
echo "successfully regridded off_gmt from 50km parameter file"     

# remove crop file
rm $crop_file $tmp1 $tmp2
