#!/bin/bash

module purge
module use /scratch2/BMC/gsd-hpcs/modman/modulefiles/base
module load cmake gcc boost openmpi

#-----------------------------------------------------------------------
# Set some directories
#-----------------------------------------------------------------------
PID=$$
TEST_DIR=$( pwd )                   # Directory with this script
TOP_DIR=${TEST_DIR}/..              # Top level directory

#-----------------------------------------------------------------------
# Build GeoFLOW
#-----------------------------------------------------------------------
mkdir ${TOP_DIR}/build && cd ${TOP_DIR}/build
# cmake -DGDIM=2 ..
cmake ..
make -j4 install
