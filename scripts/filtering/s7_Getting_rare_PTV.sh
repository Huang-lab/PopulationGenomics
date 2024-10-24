#!/bin/bash

#BSUB -J s7_Getting_rare_PTV
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 1
#BSUB -W 24:00
#BSUB -R rusage[mem=1600]
#BSUB -R span[ptile=1]
#BSUB -o s7_Getting_rare_PTV_%I.stdout
#BSUB -eo s7_Getting_rare_PTV_%I.stderr
#BSUB -L /bin/bash

ml bcftools

variants="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/S6_Filtered_ACMG32_truncations_PTV/s6_Sema4_Filtered_ACMG32_truncations_PTV.vcf.gz"
chromosome=$1
vcf_in="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/S5_Filtered_AF005/s5_Filtered_AF_chrALL.sort.vcf.gz"
vcf_out="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/S7_Filtered_ACMG32_truncations005/S7_Filtered_ACMG32_truncations005_chrALL.vcf.gz"

bcftools index $vcf_in
bcftools view -R $variants $vcf_in -o $vcf_out
bcftools index $vcf_out

#2nd filtering
export input_vcf="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/S7_Filtered_ACMG32_truncations005/S7_Filtered_ACMG32_truncations005_chrALL.vcf.gz"
export variants="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s3_ACMG32_cancer_gene_truncations.txt"
export output_vcf="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/S7_Filtered_ACMG32_truncations005/ACMG32_AF005_PTV_2ndfiltered.vcf"


ml python

python scripts/utils/General_2nd_filterVCF.py
