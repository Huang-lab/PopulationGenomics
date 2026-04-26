# PopulationGenomics

End-to-end population-genomics pipeline that takes joint-called WES/WGS VCFs through ANNOVAR/InterVar annotation, ACMG-cancer-gene PLP/PTV variant extraction, allele-frequency filtering, and per-cohort carrier-frequency summaries.

## Layout

```
.
├── pipeline.py                 # orchestrator: submits each stage to LSF with -w "done(<prev>)"
├── config.py                   # single source of truth for paths/tunables (env-overridable)
├── config.sh                   # same, sourced by every shell wrapper
├── requirements.txt            # runtime Python deps
├── requirements-dev.txt        # adds pytest
├── scripts/
│   ├── preprocessing/          # s1 ANNOVAR/InterVar, s2 merge annotations
│   ├── feature_extraction/     # s3 ACMG-cancer-gene PLP/PTV extraction
│   ├── filtering/              # s4..s7 (s5 = per-chrom array, s5b = concat)
│   ├── summary/                # s8 patient×variant table, s9 carrier frequencies
│   └── utils/                  # shared VCF-filter helper
└── tests/                      # pytest suite
```

## Prerequisites

- Python 3.10+ with `pandas`, `numpy` (`pip install -r requirements.txt`)
- R with `readr`, `dplyr`, `readxl`
- `bcftools`, `bgzip`
- ANNOVAR (with the `humandb/` databases referenced in `s1_run_intjob.sh`)
- InterVar 2.2.1
- LSF (the wrappers use `bsub`)

## Configuration

All cohort-specific paths and tunables live in `config.py` / `config.sh`. Defaults match the BioMe Sema4 layout under `/sc/arion/projects/rg_huangk06/variants_PLP_BioMe`. Override any value via env vars — no code changes required:

```bash
# example: run on a different cohort, write outputs to a scratch dir
export PROJECT_ROOT=/path/to/cohortX
export OUT_DIR=/scratch/run42
export INPUT_VCF_BASENAME=CohortX_WES
python pipeline.py
```

Common overrides:

| Variable | Default | Purpose |
| --- | --- | --- |
| `PROJECT_ROOT` | `/sc/arion/projects/rg_huangk06/variants_PLP_BioMe` | Top of the cohort tree |
| `DATA_DIR` | `${PROJECT_ROOT}/data` | Input VCFs |
| `OUT_DIR` | `${PROJECT_ROOT}/out` | Pipeline outputs |
| `METADATA_DIR` | `${PROJECT_ROOT}/metadata` | Patient info TSV |
| `CHROM_DIR` | `${DATA_DIR}/chromosome` | Per-chromosome split VCFs (s5 input) |
| `INTERVAR_DIR` | `${PROJECT_ROOT}/tools/InterVar-2.2.1` | InterVar install |
| `ACMG_XLSX` | (Sema4 supp xlsx) | ACMG SF v3.2 cancer gene list |
| `INPUT_VCF_BASENAME` | `BioMe_Sema4_WES` | Stem of the joint-called VCF |
| `PATIENT_INFO_NAME` | `Sema4_HX_WXS_Newgroups.tsv` | Patient metadata file under `METADATA_DIR` |
| `AF_THRESHOLD` | `0.0005` | Max allele frequency for s5's "rare site" filter |

## Running the pipeline

```bash
python pipeline.py
```

The orchestrator submits each stage with `bsub` and chains them with `-w "done(<prev>)"`, so the cluster runs them in order. Each `submit_job` call returns the LSF job-id; the next stage waits on it.

## Stages

| # | Script | What it does |
|---|--------|--------------|
| s1 | `preprocessing/s1_run_intjob.sh` | ANNOVAR/InterVar on each input VCF |
| s2 | `preprocessing/s2_Merge_annotation.{sh,R}` | Joins ANNOVAR + InterVar multianno tables on the variant key (no fragile string-paste matching) |
| s3 | `feature_extraction/s3_Extract_PLP_PTV_variants.{sh,R}` | Extracts PLP + PTV truncating variants on ACMG cancer genes |
| s4-1 | `filtering/s4_Filtering.PLP_s1.sh` | `bcftools view -R` PLP regions |
| s4-2 | `filtering/s4_Filtering.PLP_s2.sh` | Position-level second-pass filter via `utils/General_2nd_filterVCF.py` |
| s5 | `filtering/s5_Retain_rareSite_inVCF_filterbyAF.sh` | LSF array `[1-24]` (1..22, X, Y); per-chromosome AF filter |
| s5b | `filtering/s5b_Concat_filtered_chroms.sh` | Concat / sort / index the s5 array outputs |
| s6 | `filtering/s6_filterExomesByVariants_PTV.sh` | PTV regions filter on the cohort VCF |
| s7 | `filtering/s7_Getting_rare_PTV.sh` | Intersect s5b output with s6 regions, then second-pass position filter |
| s8 | `summary/s8_Generate_summary_df.{sh,py}` | Per-patient, per-variant carrier table |
| s9 | `summary/s9_Cal_carrier_Freq.{sh,py}` | Carrier frequencies by group, gene, and ancestry |

## Testing

```bash
pip install -r requirements-dev.txt
pytest tests/
```

The suite covers genotype/carrier parsing, ANNOVAR REF/ALT normalization, the central config (Python & shell agree on the same overrides), the `bsub` command shape and dependency chaining, and static invariants on the shell + R scripts (no hard-coded cohort paths leaking out of `config.sh`, every wrapper sources `config.sh`, no `ssh` inside batch jobs, `s5` reads `LSB_JOBINDEX`, `s3.R` doesn't reference its own pre-rename column names).
