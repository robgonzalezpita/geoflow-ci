#!/usr/bin/env bash

## Usage:
##
##   bash integration_tests.sh <RUN_DIR> <EXEC_NAME> <INPUT_JSON> 
##
##   Arguments: 
##       RUN_DIR    : This is the directory to run the integration test in.
##       EXEC_NAME  : Path the the geoflow_cdg executable to run.  
##       INPUT_JSON : Path to the input.jsn configuration file.
##

sbatch <<EOT
#!/bin/bash
#SBATCH --output=slurm.out
#SBATCH --error=slurm.out
#SBATCH -A gsd-hpcs
#SBATCH --exclusive
#SBATCH -q batch   
## NOTE:
## Machine   CPU Cores  GPUs
## -----------------------------
##     FGE      20       8
##   theia      22       0
##    hera      40       0
## -----------------------------
# SBATCH --job-name=testinertgrav2d
# SBATCH --ntasks=5
# SBATCH --ntasks-per-node=5
# SBATCH -t 08:00:00 
#
# Configuration
#
export RUN_DIR="$1"
export EXEC_NAME="$2"
export INPUT_JSON="$3"
export SLURM_JOB_NAME=testinertgrav2d
export SLURM_NTASKS=5
export SLURM_NTASKS_PER_NODE=5
export SLURM_TIMELIMIT=08:00:00
## Modules Needed
module purge
module use /scratch2/BMC/gsd-hpcs/modman/modulefiles/base
module load gcc
module load openmpi
module load boost
module load gptl
# 
# Set Number of OpenMP threads per Node
#
export CORES_PER_NODE=40
export OMP_NUM_THREADS=${CORES_PER_NODE}/${SLURM_NTASKS_PER_NODE}
#
# Print configuration 
#
echo "OMP_NUM_THREADS=" ${OMP_NUM_THREADS}
echo "SLURM_NTASKS=" ${SLURM_NTASKS}
echo "RUN_DIR=" ${RUN_DIR}
echo "EXEC_NAME=" ${EXEC_NAME}
echo "INPUT_JSON=" ${INPUT_JSON}
echo "SLURM_NTASKS_PER_NODE=" ${SLURM_NTASKS_PER_NODE}
#
# Create output directory
#
cd ${RUN_DIR}
rm -rf outs/
mkdir outs
#
# Run Commands
#
cd ${RUN_DIR}
srun -n ${SLURM_NTASKS} ${EXEC_NAME} -i ${INPUT_JSON} 
 
EOT
