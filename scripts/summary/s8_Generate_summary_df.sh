#!/bin/bash
set -euo pipefail

#BSUB -J Generate_summary_df.lsf
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 4
#BSUB -W 24:00
#BSUB -R rusage[mem=1600]
#BSUB -R span[hosts=1]
#BSUB -R span[ptile=1]
#BSUB -o Generate_summary_df.stdout
#BSUB -eo Generate_summary_df.stderr
#BSUB -L /bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=/dev/null
source "${REPO_ROOT}/config.sh"

ml python

cd "${REPO_ROOT}"
python scripts/summary/s8_Generate_summary_df.py
