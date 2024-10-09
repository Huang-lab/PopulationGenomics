#!/bin/bash

#BSUB -J s2_Merge_annotation_w_genotypes_vcf
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 1
#BSUB -W 24:00
#BSUB -R rusage[mem=1600]
#BSUB -R span[ptile=1]
#BSUB -o s2_Merge_annotation_w_genotypes_vcf.stdout
#BSUB -eo s2_Merge_annotation_w_genotypes_vcf.stderr
#BSUB -L /bin/bash

Rscript scripts/preprocessing/s2_Merge_annotation.R