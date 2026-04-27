#!/bin/bash
set -euo pipefail

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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=/dev/null
source "${REPO_ROOT}/config.sh"

ml bcftools

variants="${OUT_DIR}/S6_Filtered_ACMG32_truncations_PTV/s6_Sema4_Filtered_ACMG32_truncations_PTV.vcf.gz"
vcf_in="${OUT_DIR}/S5_Filtered_AF005/s5_Filtered_AF_chrALL.sort.vcf.gz"
vcf_out_dir="${OUT_DIR}/S7_Filtered_ACMG32_truncations005"
vcf_out="${vcf_out_dir}/S7_Filtered_ACMG32_truncations005_chrALL.vcf.gz"

mkdir -p "$vcf_out_dir"
bcftools index "$vcf_in"
bcftools view -R "$variants" "$vcf_in" -o "$vcf_out"
bcftools index "$vcf_out"

# 2nd filtering
export input_vcf="$vcf_out"
export variants="${OUT_DIR}/s3_ACMG32_cancer_gene_truncations.txt"
export output_vcf="${vcf_out_dir}/ACMG32_AF005_PTV_2ndfiltered.vcf"

ml python

cd "${REPO_ROOT}"
python scripts/utils/General_2nd_filterVCF.py
