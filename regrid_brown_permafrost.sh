#!/bin/bash
#PBS -N permafrost
#PBS -q serial
#PBS -A NPSCA07935YF5
#PBS -l select=1:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=01:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

# activate virtual environment
source activate pangeo

# regrid Brown et al 1997 permafrost map to grid and resolution listed

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

filename="/u/home/gergel/data/parameters/brown_permafrost/NCSCDv2_Circumpolar_WGS84_pfregion_extent_005deg.nc"
		
# regrid file
regrid_file="/u/home/gergel/data/parameters/brown_permafrost/NCSCDv2_Circumpolar_WGS84_pfregion_extent_005deg_${grid}.nc"

cdo remapnn,$domain_file $filename $regrid_file
echo "successfully regridded Brown et al 1997 permafrost/no permafrost map to RASM grid"
