#!/bin/bash
set -euo pipefail

#BSUB -J s6_filterExomesByVariants_PTV
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 1
#BSUB -W 24:00
#BSUB -R rusage[mem=1600]
#BSUB -R span[ptile=1]
#BSUB -o s6_filterExomesByVariants_PTV.stdout
#BSUB -eo s6_filterExomesByVariants_PTV.stderr
#BSUB -L /bin/bash

ml bcftools

variants='/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s3_ACMG32_cancer_gene_truncations_regions.txt'
vcf_in="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/data/BioMe_Sema4_WES.vcf.gz"
vcf_out="/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/S6_Filtered_ACMG32_truncations_PTV/s6_Sema4_Filtered_ACMG32_truncations_PTV.vcf.gz"

mkdir -p "$(dirname "$vcf_out")"
bcftools view -R "$variants" "$vcf_in" > "$vcf_out"
