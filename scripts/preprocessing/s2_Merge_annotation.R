#!/usr/bin/env Rscript

# Merges ANNOVAR and InterVar multianno tables on the canonical variant key
# (Chr, Start, End, Ref, Alt) plus gene/function context. The join is done
# with dplyr::full_join rather than match(paste(...)), so a stray space or
# delimiter inside any field can't produce false matches.
#
# Inputs come from env vars (set by the wrapper shell script that sources
# config.sh). The output basename mirrors the input VCF basename.

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
})

env_or_stop <- function(name, default = NULL) {
  v <- Sys.getenv(name, unset = NA)
  if (is.na(v) || v == "") {
    if (is.null(default)) stop(sprintf("env var %s is required", name))
    return(default)
  }
  v
}

out_dir <- env_or_stop("OUT_DIR")
basename <- env_or_stop("INPUT_VCF_BASENAME")

annovar_path  <- file.path(out_dir, paste0(basename, ".variants.intervar.vcf.hg38_multianno.txt"))
intervar_path <- paste0(annovar_path, ".intervar")
output_path   <- file.path(out_dir, "s2_Merge_intervar_annovar_multianno.txt")

annovar  <- read_delim(annovar_path,  delim = "\t", col_types = cols())
intervar <- read_delim(intervar_path, delim = "\t", col_types = cols())
colnames(intervar)[1] <- "Chr"

# Strip any rows where the header row was repeated mid-file.
annovar  <- annovar[annovar$Chr != "Chr", ]
intervar <- intervar[intervar$Chr != "#Chr", ]

# Normalize the InterVar evidence column: " InterVar: Pathogenic PVS1=..." -> "Pathogenic"
intervar$InterVar..InterVar.and.Evidence <- sub(
  " PS=.*$", "",
  sub("^ InterVar: ", "", intervar$InterVar..InterVar.and.Evidence)
)

# InterVar names the gene column Ref.Gene; ANNOVAR names it Gene.refGene.
intervar <- dplyr::rename(intervar, Gene.refGene = Ref.Gene)

key_cols <- c("Chr", "Start", "End", "Ref", "Alt", "Gene.refGene", "Func.refGene", "ExonicFunc.refGene")
ann <- dplyr::full_join(annovar, intervar, by = key_cols)

colnames(ann) <- make.names(colnames(ann), unique = TRUE)
colnames(ann) <- sub("InterVar..InterVar.and.Evidence", "InterVar_automated", colnames(ann))

write_delim(ann, output_path, delim = "\t")
