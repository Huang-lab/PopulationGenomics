# PopulationGenomics

### Workflow Steps
#### This workflow orchestrates a series of scripts for preprocessing, annotation, feature extraction, filtering, and summarizing variants.


### Preprocessing
- **scripts/preprocessing/s1_run_intjob.sh**: This script runs AnnoVar/InterVar the initial job for Mount Sinai BioMe cohort II.

### Annotation
- **scripts/preprocessing/s2_Merge_annotation.R**: This R script merges AnnoVar/InterVar annotations.

### Feature Extraction
- **scripts/feature_extraction/s3_Extract_PLP_PTV_variants.R**: This R script extracts PLP and PTV variants on cancer genes based on ACMG/AMP guidelines.

### Filtering
- **scripts/filtering/s4_Filtering.PLP_s1.sh**: This script filters PLP positions.
- **scripts/filtering/s4_Filtering.PLP_s2.sh**: This script performs additional filtering on PLP variants (ref alt).
- **scripts/filtering/s5_Retain_rareSite_inVCF_filterbyAF.sh**: This script retains rare sites in VCF files filtered by Allele Frequency 0.05% (0.0005). Submit as a job array `[1-24]`; each task filters one chromosome (1..22, X, Y).
- **scripts/filtering/s5b_Concat_filtered_chroms.sh**: Concatenates, sorts, and indexes the per-chromosome outputs from s5. Submit after the s5 array finishes.
- **scripts/filtering/s6_filterExomesByVariants_PTV.sh**: This script filters exomes by PTV variants.
- **scripts/filtering/s7_Getting_rare_PTV.sh**: This script gets rare PTV variants.

### summary_df
- **scripts/summary/s8_Generate_summary_df.py**: This script generates a summary df for variants patients.
- **scripts/summary/s9_Cal_carrier_Freq.py**: This script Calculates carrier freq by Groups.
