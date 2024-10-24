#!/usr/bin/env Rscript

library(readr)
library(xlsx)

ann <- read_delim('/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s2_Merge_intervar_annovar_multianno.txt', delim = '\t', col_types = cols())

cols_keep <- c('Chr', 'Start', 'Ref', 'Alt', 'Ref.Gene', 'InterVar_automated', 'CLNSIG', 'ExonicFunc.refGene', 'Func.refGene', 'ExonicFunc.knownGene')
ann_subset <- ann[, cols_keep]
colnames(ann_subset) <- c('#CHROM', 'POS', 'REF', 'ALT', 'Ref.Gene', 'InterVar_automated', 'CLNSIG', 'ExonicFunc_refGene', 'Func_refGene', 'ExonicFunc_knownGene')

write_delim(ann_subset, '/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s2_Merge_intervar_annovar_multianno_simple.txt', delim = '\t')

ann_plp <- ann_subset[ann_subset$InterVar_automated %in% c('Pathogenic PVS1=0', 'Pathogenic PVS1=1', 'Likely pathogenic PVS1=0', 'Likely pathogenic PVS1=1'), ]
write_delim(ann_plp, '/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s2_all_PLP_list.txt', delim = '\t')

acm <- read.xlsx('/sc/arion/projects/rg_huangk06/variantDisease/data/cancer/ACMG_SF_v32_supp.xlsx', sheetIndex = 1, startRow = 3, endRow = 100)
acm <- acm[acm$Phenotype.Category == 'Cancer', ]

ann_plp_predis_cancer <- ann_plp[ann_plp$Ref.Gene %in% acm$Gene, ]
write_delim(ann_plp_predis_cancer, '/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s3_ACMG32_cancer_gene.predis.plp.txt', delim = '\t')

ann_tru <- ann_subset[(ann_subset$ExonicFunc.refGene %in% c('nonframeshift deletion', 'nonframeshift insertion', 'frameshift deletion', 'frameshift insertion', 'stopgain', 'stoploss', 'startloss')) | (ann_subset$Func.refGene %in% c('exonic;splicing', 'ncRNA_exonic;splicing', 'ncRNA_splicing', 'splicing')), ]

conflict_list <- c('Benign PVS1=0', 'Benign PVS1=1', 'Likely benign PVS1=0', 'Likely benign PVS1=1', 'Likely benign', 'Benign', 'Benign/Likely_benign', 'Likely_benign', 'Benign', 'benign', 'likely_benign', 'Likely_Benign', 'Likely_benign/Benign')

ann_tru_filtered <- ann_tru[!(ann_tru$CLNSIG %in% conflict_list | ann_tru$InterVar_automated %in% conflict_list), ]

ann_tru_cancer <- ann_tru_filtered[ann_tru_filtered$Ref.Gene %in% acm$Gene, ]
sub_tru <- ann_tru_cancer[, c('#CHROM', 'POS')]

write_delim(sub_tru, '/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s3_ACMG32_cancer_gene_truncations_regions.txt', delim = '\t')
write_delim(ann_tru_cancer, '/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s3_ACMG32_cancer_gene_truncations.txt', delim = '\t')
