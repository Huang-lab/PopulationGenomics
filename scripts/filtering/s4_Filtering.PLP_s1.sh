#!/bin/bash
set -euo pipefail

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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=/dev/null
source "${REPO_ROOT}/config.sh"

ml bcftools

variants="${OUT_DIR}/s3_ACMG32_cancer_gene.predis.plp.txt"
vcf_in="${DATA_DIR}/${INPUT_VCF_BASENAME}.vcf.gz"
vcf_out="${OUT_DIR}/s4_BioMe_Sema4_FilterExomesByPre.PLP.vcf"

bcftools view -R "$variants" "$vcf_in" > "$vcf_out"
