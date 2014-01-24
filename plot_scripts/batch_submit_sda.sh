#!/bin/bash

# Batch qsub submission script to calculate homogeneity test results for each reduced data file 

arr=(`ls $SCRATCH/gpu_models/SdA/reduced_data/40`)
len=${#arr[*]}

for((i=0; i<=$len; i+=1 ))
do
    infile=${arr[$i]}
    qsub submit_sda_et.sh -v REDUCEDFILE="$infile"
    sleep 5   
done

