#!/bin/bash
#PBS -N geotiff
#PBS -q serial
#PBS -A NPSCA07935YF5
#PBS -l select=1:ncpus=32:mpiprocs=8:mem=200GB
#PBS -l walltime=12:00:00
#PBS -j oe
#PBS -M gergel@uw.edu
#PBS -m abe

source activate pangeo

python /u/home/gergel/scripts/batch_convert_worldclim_geotiffs_to_netcdfs.py
