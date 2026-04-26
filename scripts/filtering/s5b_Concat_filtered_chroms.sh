#!/bin/bash
set -euo pipefail

#BSUB -J s5b_Concat_filtered_chroms
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 1
#BSUB -W 24:00
#BSUB -R rusage[mem=3200]
#BSUB -R span[ptile=1]
#BSUB -o s5b_Concat_filtered_chroms.stdout
#BSUB -eo s5b_Concat_filtered_chroms.stderr
#BSUB -L /bin/bash

ml bcftools

out_dir="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/S5_Filtered_AF005"
cd "$out_dir"

export TMPDIR="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/scripts/tmp"
mkdir -p "$TMPDIR"

bcftools concat s5_Filtered_AF_chr*.vcf.gz -Oz -o s5_Filtered_AF_chrALL.vcf.gz
bcftools sort -Oz -o s5_Filtered_AF_chrALL.sort.vcf.gz s5_Filtered_AF_chrALL.vcf.gz
bcftools index s5_Filtered_AF_chrALL.sort.vcf.gz
