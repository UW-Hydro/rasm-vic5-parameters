#!/bin/bash
#PBS -N geotiff_convert
#PBS -q serial
#PBS -A NPSCA07935YF5
#PBS -l select=1:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=12:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

source activate pangeo

python /u/home/gergel/scripts/rasm-vic5-parameters/batch_convert_soilgrid_geotiff_to_netcdf.py 
