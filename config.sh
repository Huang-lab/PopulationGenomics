# Source this from any pipeline shell script:
#     SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#     REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
#     source "${REPO_ROOT}/config.sh"
#
# Every variable below is set with `:=` so callers can override individual
# values from the environment (e.g. `OUT_DIR=/run42 ./pipeline.py`).

: "${PROJECT_ROOT:=/sc/arion/projects/rg_huangk06/variants_PLP_BioMe}"
: "${DATA_DIR:=${PROJECT_ROOT}/data}"
: "${OUT_DIR:=${PROJECT_ROOT}/out}"
: "${METADATA_DIR:=${PROJECT_ROOT}/metadata}"
: "${CHROM_DIR:=${DATA_DIR}/chromosome}"
: "${INTERVAR_DIR:=${PROJECT_ROOT}/tools/InterVar-2.2.1}"
: "${TMPDIR:=${REPO_ROOT}/scripts/tmp}"

: "${ACMG_XLSX:=/sc/arion/projects/rg_huangk06/variantDisease/data/cancer/ACMG_SF_v32_supp.xlsx}"

: "${INPUT_VCF_BASENAME:=BioMe_Sema4_WES}"
: "${PATIENT_INFO_NAME:=Sema4_HX_WXS_Newgroups.tsv}"
: "${AF_THRESHOLD:=0.0005}"

export PROJECT_ROOT DATA_DIR OUT_DIR METADATA_DIR CHROM_DIR INTERVAR_DIR TMPDIR
export ACMG_XLSX INPUT_VCF_BASENAME PATIENT_INFO_NAME AF_THRESHOLD
