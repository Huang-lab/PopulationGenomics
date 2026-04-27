#!/bin/bash
set -euo pipefail

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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=/dev/null
source "${REPO_ROOT}/config.sh"

export input_vcf="${OUT_DIR}/s4_BioMe_Sema4_FilterExomesByPre.PLP.vcf"
export variants="${OUT_DIR}/s3_ACMG32_cancer_gene.predis.plp.txt"
export output_vcf="${OUT_DIR}/s4_2nd_filter_PLP.vcf"

ml python

cd "${REPO_ROOT}"
python scripts/utils/General_2nd_filterVCF.py
