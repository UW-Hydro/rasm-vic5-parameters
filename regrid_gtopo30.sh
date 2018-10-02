#!/bin/bash
#PBS -N gtopo_regrid
#PBS -q x11
#PBS -A NPSCA07935YF5
#PBS -l select=1:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=12:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

# regrid GTOPO DEM to domain file listed 

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

filename="/u/home/gergel/data/parameters/gtopo30/sdat_10003_1_20180525_151136146.nc"
		
# crop file
crop_file="/u/home/gergel/data/parameters/gtopo30/cropped_dem.nc"
cdo -sellonlatbox,-180,180,15,90 -selname,Band1 $filename $crop_file

# regrid file
tmp1="/u/home/gergel/data/parameters/gtopo30/sdat_10003_1_20180525_151136146_tmp.nc"
tmp2="/u/home/gergel/data/parameters/gtopo30/sdat_10003_1_20180525_151136146_${grid}_tmp.nc"
regrid_file="/u/home/gergel/data/parameters/gtopo30/sdat_10003_1_20180525_151136146_${grid}.nc"

# set fillvalues to missing values to avoid incorrect remapping of coastal gridcells, 
# solution adapted from https://code.mpimet.mpg.de/boards/2/topics/6172?r=6199
cdo -setvrange,-1000,1000 $crop_file $tmp1
cdo setmisstonn $tmp1 $tmp2

# remap both land and ocean gridcells so that coastal gridcells are assigned valid values
cdo remapnn,$domain_file $tmp2 $regrid_file
echo "successfully regridded GTOPO30 0.05 deg Digital Elevation Map (DEM)"	
	
# remove crop file
rm $crop_file $tmp1 $tmp2
