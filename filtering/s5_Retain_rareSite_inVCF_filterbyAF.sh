#!/bin/bash

#BSUB -J s5_Retain_rareSite_inVCF_filterbyAF[1-24]
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 1
#BSUB -W 24:00
#BSUB -R rusage[mem=1600]
#BSUB -R span[ptile=1]
#BSUB -o s5_Retain_rareSite_inVCF_filterbyAF_%I.stdout
#BSUB -eo s5_Retain_rareSite_inVCF_filterbyAF_%I.stderr
#BSUB -L /bin/bash

ml bcftools

chromosome=$1
vcf_in="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/data/chromosome/split.$chromosome.vcf.gz"
vcf_out="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/S5_Filtered_AF005/s5_Filtered_AF_chr$chromosome.vcf.gz"

bcftools view --max-af 0.0005 "$vcf_in" | bgzip -c > "$vcf_out"

# Concatenate all chromosome VCF files into one
cd /sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/S5_Filtered_AF005/

export TMPDIR=/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/scripts/tmp
mkdir -p "$TMPDIR"

# Concatenate the chromosome VCF files
bcftools concat s5_Filtered_AF_chr*.vcf.gz -Oz -o s5_Filtered_AF_chrALL.vcf.gz

# Sort the concatenated VCF file if necessary (only if the input files were not already sorted)
bcftools sort -Oz -o s5_Filtered_AF_chrALL.sort.vcf.gz s5_Filtered_AF_chrALL.vcf.gz

# Index the sorted VCF file
bcftools index s5_Filtered_AF_chrALL.sort.vcf.gz
