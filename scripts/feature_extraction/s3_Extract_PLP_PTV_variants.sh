#!/bin/bash
set -euo pipefail

#BSUB -J s3_Extract_PLP_PTV_variants
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 1
#BSUB -W 24:00
#BSUB -R rusage[mem=1600]
#BSUB -R span[ptile=1]
#BSUB -o s3_Extract_PLP_PTV_variants.stdout
#BSUB -eo s3_Extract_PLP_PTV_variants.stderr
#BSUB -L /bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=/dev/null
source "${REPO_ROOT}/config.sh"

cd "${REPO_ROOT}"
Rscript scripts/feature_extraction/s3_Extract_PLP_PTV_variants.R
