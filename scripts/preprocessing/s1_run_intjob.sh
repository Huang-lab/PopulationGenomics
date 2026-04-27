#!/bin/bash
set -euo pipefail

#BSUB -J s1_run_intjob_sema4
#BSUB -P acc_DiseaseGeneCell
#BSUB -q premium
#BSUB -n 2
#BSUB -W 24:00
#BSUB -R rusage[mem=3200]
#BSUB -R span[ptile=1]
#BSUB -o s1_run_intjob_sema4.stdout
#BSUB -eo s1_run_intjob_sema4.stderr
#BSUB -L /bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=/dev/null
source "${REPO_ROOT}/config.sh"

ml python
cd "${INTERVAR_DIR}"

procd=("${OUT_DIR}"/*.avinput)

for filename in "${DATA_DIR}"/*.vcf.gz; do
    base="$(basename "$filename")"
    if [[ "${procd[*]}" =~ ${base}.avinput ]]; then
        echo "${base} ---- done!"
    else
        echo "${base} ---- PROCESSING..."
        stem="$(basename "${filename%.vcf.gz}")"
        zcat "${DATA_DIR}/${base%.gz}" | awk '{ for (i = 1; i <= 8; ++i) printf $i"\t"; print "" }' > "${DATA_DIR}/${stem}.variants.vcf"
        # Make sure to download and use the latest database for ANNOVAR. See:
        # https://annovar.openbioinformatics.org/en/latest/user-guide/download/#additional-databases
        perl table_annovar.pl "${DATA_DIR}/${stem}.variants.vcf" humandb/ -buildver hg38 -out "${OUT_DIR}/${stem}.variants.vcf" -remove -protocol refGene,ensGene,knowngene,gnomad41_genome,exac03,avsnp151,dbnsfp47,dbscsnv11,clinvar_20240917,dbnsfp47a_interpro -operation g,g,g,f,f,f,f,f,f,f -vcfinput -polish

        python Intervar.py -b hg38 -t intervardb -i "${DATA_DIR}/${stem}.variants.vcf" --input_type=VCF -o "${OUT_DIR}/${stem}.variants.intervar.vcf"
    fi
done
