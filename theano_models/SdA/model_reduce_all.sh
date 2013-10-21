#!/bin/bash

# Batch qsub submission script to produce reduced data for each model of SdA

arr=(`ls $SCRATCH/gpu_models/SdA/finetune_pkl_files/batch_1000_size_25ch_mom_0.8_wd_0.00001_lr_0.005`)
len=${#arr[*]}

for((i=1; i<=$len; i+=2 ))
do
    let prev=$i-1
    first=${arr[$i]}
    second=${arr[$prev]}
    qsub submit_reduce_gravity.sh -v FIRSTMODEL="$first",SECONDMODEL="$second"
    sleep 5   
done