#!/bin/bash
set -euo pipefail

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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=/dev/null
source "${REPO_ROOT}/config.sh"

ml bcftools

# Map LSF array index 1..24 to chromosomes 1..22, X (23), Y (24).
idx="${LSB_JOBINDEX:?LSB_JOBINDEX must be set; submit as a job array}"
case "$idx" in
    23) chromosome="X" ;;
    24) chromosome="Y" ;;
    *)  chromosome="$idx" ;;
esac

vcf_in="${CHROM_DIR}/split.${chromosome}.vcf.gz"
vcf_out_dir="${OUT_DIR}/S5_Filtered_AF005"
vcf_out="${vcf_out_dir}/s5_Filtered_AF_chr${chromosome}.vcf.gz"

mkdir -p "$vcf_out_dir"
bcftools view --max-af "${AF_THRESHOLD}" "$vcf_in" | bgzip -c > "$vcf_out"
