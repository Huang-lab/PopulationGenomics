#!/bin/bash

#BSUB -J 2nd_filter.lsf
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 4
#BSUB -W 144:00
#BSUB -R rusage[mem=1600]
#BSUB -R span[hosts=1]
#BSUB -R span[ptile=1]
#BSUB -o 2nd_filter.PLP.stdout
#BSUB -eo 2nd_filter.PLP.stderr
#BSUB -L /bin/bash

export input_vcf="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s4_BioMe_Sema4_FilterExomesByPre.PLP.vcf"
export variants="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s3_ACMG32_cancer_gene.predis.plp.txt"
export output_vcf="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s4_2nd_filter_PLP.vcf"

ml python

python scripts/utils/General_2nd_filterVCF.py
