#!/bin/bash

#BSUB -J Cal_freq_df.lsf
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 2
#BSUB -W 60:00
#BSUB -R rusage[mem=1600]
#BSUB -R span[hosts=1]
#BSUB -R span[ptile=1]
#BSUB -o Cal_freq_df.stdout
#BSUB -eo Cal_freq_df.stderr
#BSUB -L /bin/bash



ml python

python scripts/summary/s9_Cal_carrier_Freq.py
