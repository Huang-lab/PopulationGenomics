#!/usr/bin/env Rscript

library(readr)

path_out <- '/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/'
annovar_path <- 'BioMe_Sema4_WES.variants.intervar.vcf.hg38_multianno.txt'
intervar_path <- 'BioMe_Sema4_WES.variants.intervar.vcf.hg38_multianno.txt.intervar'

annovar <- read_delim(paste0(path_out, annovar_path), delim = '\t', col_types = cols())
intervar <- read_delim(paste0(path_out, intervar_path), delim = '\t', col_types = cols())
colnames(intervar)[1] <- 'Chr'

annovar <- annovar[annovar$Chr != 'Chr', ]
intervar <- intervar[intervar$Chr != '#Chr', ]

intervar$InterVar..InterVar.and.Evidence <- sub(' PS=.*$', '', sub('^ InterVar: ', '', intervar$InterVar..InterVar.and.Evidence))

colnames(intervar) <- paste0("intervar.", colnames(intervar))
intervar$intervar.Chr <- sub("^#", "", intervar$intervar.Chr)

map <- match(paste(annovar$Chr, annovar$Start, annovar$End, annovar$Ref, annovar$Alt, annovar$Gene.refGene, annovar$Func.refGene, annovar$ExonicFunc.refGene), paste(intervar$intervar.Chr, intervar$intervar.Start, intervar$intervar.End, intervar$intervar.Ref, intervar$intervar.Alt, intervar$intervar.Ref.Gene, intervar$intervar.Func.refGene, intervar$intervar.ExonicFunc.refGene))

ann <- cbind(annovar[!is.na(map), ], intervar[map[!is.na(map)], ])
idx.unq.ann <- which(is.na(map))
idx.unq.int <- setdiff(seq_len(nrow(intervar)), map)

ann <- rbind(ann, cbind(annovar[idx.unq.ann, ], setNames(as.data.frame(matrix(NA, length(idx.unq.ann), ncol(intervar))), colnames(intervar))))
ann <- rbind(ann, cbind(setNames(as.data.frame(matrix(NA, length(idx.unq.int), ncol(annovar))), colnames(annovar)), intervar[idx.unq.int, ]))
colnames(ann) <- make.names(colnames(ann), unique = TRUE)
colnames(ann) <- sub('intervar\\.InterVar\\.\\.InterVar\\.and\\.Evidence', 'InterVar_automated', colnames(ann))

write_delim(ann, '/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out/s2_Merge_intervar_annovar_multianno.txt', delim = '\t')
