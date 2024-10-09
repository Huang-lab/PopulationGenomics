#!/bin/bash

#BSUB -J s4_Filtering_PLP_s1
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 2
#BSUB -W 24:00
#BSUB -R rusage[mem=1600]
#BSUB -R span[ptile=1]
#BSUB -o s4_Filtering_PLP_s1.stdout
#BSUB -eo s4_Filtering_PLP_s1.stderr
#BSUB -L /bin/bash

ssh regen2
ml bcftools

variants='/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s3_ACMG32_cancer_gene.predis.plp.txt'
vcf_in="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/data/BioMe_Sema4_WES.vcf.gz"
vcf_out="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s4
