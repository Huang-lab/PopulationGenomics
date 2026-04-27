#!/usr/bin/env Rscript

# Extract PLP variants and PTV truncating-variant regions on ACMG cancer
# genes from the merged annovar/intervar table produced by s2.
#
# Inputs come from env vars (set by the wrapper shell script that sources
# config.sh).

suppressPackageStartupMessages({
  library(readr)
  library(readxl)
})

env_or_stop <- function(name) {
  v <- Sys.getenv(name, unset = NA)
  if (is.na(v) || v == "") stop(sprintf("env var %s is required", name))
  v
}

out_dir   <- env_or_stop("OUT_DIR")
acmg_xlsx <- env_or_stop("ACMG_XLSX")

merged_path <- file.path(out_dir, "s2_Merge_intervar_annovar_multianno.txt")
ann <- read_delim(merged_path, delim = "\t", col_types = cols())

cols_keep <- c(
  "Chr", "Start", "Ref", "Alt", "Gene.refGene", "InterVar_automated",
  "CLNSIG", "ExonicFunc.refGene", "Func.refGene", "ExonicFunc.knownGene"
)
ann_subset <- ann[, cols_keep]
colnames(ann_subset) <- c(
  "#CHROM", "POS", "REF", "ALT", "Ref.Gene", "InterVar_automated",
  "CLNSIG", "ExonicFunc_refGene", "Func_refGene", "ExonicFunc_knownGene"
)

write_delim(ann_subset, file.path(out_dir, "s2_Merge_intervar_annovar_multianno_simple.txt"), delim = "\t")

plp_labels <- c(
  "Pathogenic PVS1=0", "Pathogenic PVS1=1",
  "Likely pathogenic PVS1=0", "Likely pathogenic PVS1=1"
)
ann_plp <- ann_subset[ann_subset$InterVar_automated %in% plp_labels, ]
write_delim(ann_plp, file.path(out_dir, "s2_all_PLP_list.txt"), delim = "\t")

acm <- read_excel(acmg_xlsx, sheet = 1, skip = 2, n_max = 97)
acm <- acm[acm$`Phenotype Category` == "Cancer", ]

ann_plp_predis_cancer <- ann_plp[ann_plp$Ref.Gene %in% acm$Gene, ]
write_delim(ann_plp_predis_cancer, file.path(out_dir, "s3_ACMG32_cancer_gene.predis.plp.txt"), delim = "\t")

truncating_exonic <- c(
  "nonframeshift deletion", "nonframeshift insertion",
  "frameshift deletion", "frameshift insertion",
  "stopgain", "stoploss", "startloss"
)
splicing <- c("exonic;splicing", "ncRNA_exonic;splicing", "ncRNA_splicing", "splicing")

# Use the renamed columns (ExonicFunc_refGene / Func_refGene). Original code
# referenced ExonicFunc.refGene / Func.refGene, which are NULL after the
# rename above and produced an empty truncations file.
ann_tru <- ann_subset[
  (ann_subset$ExonicFunc_refGene %in% truncating_exonic) |
    (ann_subset$Func_refGene %in% splicing),
]

conflict_list <- c(
  "Benign PVS1=0", "Benign PVS1=1",
  "Likely benign PVS1=0", "Likely benign PVS1=1",
  "Likely benign", "Benign", "Benign/Likely_benign", "Likely_benign",
  "benign", "likely_benign", "Likely_Benign", "Likely_benign/Benign"
)

ann_tru_filtered <- ann_tru[
  !(ann_tru$CLNSIG %in% conflict_list | ann_tru$InterVar_automated %in% conflict_list),
]

ann_tru_cancer <- ann_tru_filtered[ann_tru_filtered$Ref.Gene %in% acm$Gene, ]
sub_tru <- ann_tru_cancer[, c("#CHROM", "POS")]

write_delim(sub_tru, file.path(out_dir, "s3_ACMG32_cancer_gene_truncations_regions.txt"), delim = "\t")
write_delim(ann_tru_cancer, file.path(out_dir, "s3_ACMG32_cancer_gene_truncations.txt"), delim = "\t")
