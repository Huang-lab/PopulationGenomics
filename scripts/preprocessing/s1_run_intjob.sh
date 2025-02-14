#!/bin/bash

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

ml python
cd /sc/arion/projects/rg_huangk06/variants_PLP_BioMe/tools/InterVar-2.2.1/
procd=(/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/*.avinput)
datafolder=/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/data
outfolder=/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out

for filename in /sc/arion/projects/rg_huangk06/variants_PLP_BioMe/data/*.vcf.gz; do
    if [[ "${procd[*]}" =~ "$(basename "$filename").avinput" ]]; then
        echo "$(basename "$filename") ---- done!"
    else
        echo "$(basename "$filename") ---- PROCESSING..."
        zcat ${datafolder}/$(basename "${filename%.gz*}") | awk '{ for (i = 1; i <= 8; ++i) printf $i"\t"; print "" }' > ${datafolder}/$(basename "${filename%.vcf.gz*}").variants.vcf
        #make sure download and use the latest database for ANNOVAR, can refer https://annovar.openbioinformatics.org/en/latest/user-guide/download/#additional-databases
        #perl table_annovar.pl ${datafolder}/$(basename "${filename%.vcf.gz*}").variants.vcf humandb/ -buildver hg38 -out ${outfolder}/$(basename "${filename%.vcf.gz*}").variants.vcf -remove -protocol refGene,ensGene,knowngene,gnomad312_genome,exac03,avsnp150,dbnsfp42c,dbscsnv11,clinvar_20221231,dbnsfp31a_interpro -operation g,g,g,f,f,f,f,f,f,f -vcfinput -polish
        perl table_annovar.pl ${datafolder}/$(basename "${filename%.vcf.gz*}").variants.vcf humandb/ -buildver hg38 -out ${outfolder}/$(basename "${filename%.vcf.gz*}").variants.vcf -remove -protocol refGene,ensGene,knowngene,gnomad41_genome,exac03,avsnp151,dbnsfp47,dbscsnv11,clinvar_20240917,dbnsfp47a_interpro -operation g,g,g,f,f,f,f,f,f,f -vcfinput -polish
        
        python Intervar.py -b hg38 -t intervardb -i ${datafolder}/$(basename "${filename%.vcf.gz*}").variants.vcf --input_type=VCF -o ${outfolder}/$(basename "${filename%.vcf.gz*}").variants.intervar.vcf
    fi
done
