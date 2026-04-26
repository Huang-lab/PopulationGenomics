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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=/dev/null
source "${REPO_ROOT}/config.sh"

ml bcftools

out_dir="${OUT_DIR}/S5_Filtered_AF005"
cd "$out_dir"

mkdir -p "$TMPDIR"

bcftools concat s5_Filtered_AF_chr*.vcf.gz -Oz -o s5_Filtered_AF_chrALL.vcf.gz
bcftools sort -Oz -o s5_Filtered_AF_chrALL.sort.vcf.gz s5_Filtered_AF_chrALL.vcf.gz
bcftools index s5_Filtered_AF_chrALL.sort.vcf.gz
