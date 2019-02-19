#!/bin/bash
#PBS -N lai_ncar
#PBS -q parallel
#PBS -A NPSCA07935YF5
#PBS -l select=2:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=18:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

# regrid LAI to domain file listed 

# grid options: 50km: wr50a_ar9v4, 25km: wr25b_ar9v4, 12km: ncar
grid="ncar"

if [ "$grid" == "wr50a_ar9v4" ]
then
        domain_file="/u/home/gergel/data/parameters/domain.lnd.wr50a_ar9v4.100920.nc"
	res="50km"
elif [ "$grid" == "wr25b_ar9v4" ]
then
        domain_file="/u/home/gergel/data/parameters/domain.lnd.wr25b_ar9v4.170413.nc"
	res="25km"
elif [ "$grid" == "ncar" ]
then 
	domain_file="/u/home/gergel/data/parameters/alaska_vic_domain_ncar.nc"
	res="12km"
else
        echo "this hasn't been defined yet"
fi

echo "grid is ${grid}"
echo "using $domain_file for regridding"


filename="/u/home/gergel/data/parameters/lai/mksrf_lai_78pfts_simyr2005.c170413_mod_fillval.nc"
		
# crop file
crop_file="/u/home/gergel/data/parameters/lai/cropped_lai_${grid}.nc"
cdo -sellonlatbox,-180,180,15,90 -selname,MONTHLY_LAI $filename $crop_file

# regrid file
tmp1="/u/home/gergel/data/parameters/lai/regridded_lai/lai_tmp_${grid}.nc"
tmp2="/u/home/gergel/data/parameters/lai/regridded_lai/lai_${grid}_tmp.nc"
regrid_file="/u/home/gergel/data/parameters/lai/regridded_lai/mksrf_lai_78pfts_simyr2005.c170413_${grid}_lai.nc"

# set fillvalues to missing values to avoid incorrect remapping of coastal gridcells, 
# solution adapted from https://code.mpimet.mpg.de/boards/2/topics/6172?r=6199
cdo -setvrange,0.0,7 $crop_file $tmp1
cdo setmisstonn $tmp1 $tmp2

# remap both land and ocean gridcells so that coastal gridcells are assigned valid values
cdo remapnn,$domain_file $tmp2 $regrid_file
echo "successfully regridded lai"	
	
# remove crop file
rm $crop_file $tmp1 $tmp2
