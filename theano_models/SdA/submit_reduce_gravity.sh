#!/bin/bash
# Torque submission script for SciNet gravity
#
# N.B: PBS lines are interpreted by qsub.  Change these defaults as 
# required
#
#PBS -l nodes=1:ppn=12:gpus=2,walltime=3:00:00
#PBS -N ReduceStackedAutoencoder
#PBS -q gravity

# Run the job

# To make substitutions from a higher up script: -p $FIRSTMODEL -q $SECONDMODEL -o $OFFSET
cd $PBS_O_WORKDIR
python reduce_SdA_multiproc.py -d "${SCRATCH}/gpu_models/SdA/reduced_data" -x "10" -p $FIRSTMODEL -q $SECONDMODEL -i "${SCRATCH}/sm_rep1_data/sample.h5" 



