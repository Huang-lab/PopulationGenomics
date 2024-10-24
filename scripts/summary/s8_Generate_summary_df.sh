#!/bin/bash

#BSUB -J Generate_summary_df.lsf
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 4
#BSUB -W 24:00
#BSUB -R rusage[mem=1600]
#BSUB -R span[hosts=1]
#BSUB -R span[ptile=1]
#BSUB -o Generate_summary_df.stdout
#BSUB -eo Generate_summary_df.stderr
#BSUB -L /bin/bash



ml python

python scripts/summary/s8_Generate_summary_df.py
