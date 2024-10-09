# PopulationGenomics

### Workflow Steps This workflow orchestrates a series of scripts for preprocessing, annotation, feature extraction, filtering, and summarizing variants.


### Preprocessing
- **s1_run_intjob.sh**: This script runs AnnoVar/InterVar the initial job for Mount Sinai BioMe cohort II (Sema4).

### Annotation
- **s2_Merge_annotation_vcf.R**: This R script merges AnnoVar/InterVar annotations.

### Feature Extraction
- **s3_Extract_PLP_PTV_variants.R**: This R script extracts PLP and PTV variants on cancer genes based on ACMG/AMP guideline.

### Filtering
- **s4_Filtering.PLP_s1.sh**: This script filters PLP positions.
- **s4_Filtering.PLP_s2.sh**: This script performs additional filtering on PLP variants (ref alt).
- **s5_Retain_rareSite_inVCF_filterbyAF.sh**: This script retains rare sites in VCF files filtered by Alle Frequency 0.05% (0.0005).
- **s6_filterExomesByVariants_PTV.sh**: This script filters exomes by PTV variants.
- **s7_Getting_rare_PTV.sh**: This script gets rare PTV variants.

### summary_df
- **s8_Generate_summary_df.py**: This script generates a summary df for variants patients.
- **s9_Cal_carrier_Freq.py**: This script Calculates carrier freq by Groups.
