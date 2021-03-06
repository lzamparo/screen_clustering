#!/bin/bash
# Torque submission script for SciNet ARC
#
# N.B: PBS lines are interpreted by qsub.  Change these defaults as 
# required
#
#PBS -l nodes=1:ppn=8:gpus=1,walltime=14:00:00
#PBS -N StackedAutoencoder
#PBS -q arc

# Load theano modules
#cd ~/jobscripts
#sh load_theano_modules.sh

# Run the job
cd $PBS_O_WORKDIR
python pretrain_SdA.py -d "${SCRATCH}/gpu_tests/SdA_results" -c 0.10 -a 1000-600-200-50 -r SdA_1000_600__200_50.pkl -s SdA_1000_600__200_50.pkl -i "${SCRATCH}/sm_rep1_data/sm_rep1_screen.h5" -o 3



SdA_1000_600__200_50.pkl
