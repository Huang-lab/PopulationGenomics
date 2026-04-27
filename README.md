# PopulationGenomics

End-to-end population-genomics pipeline that takes joint-called WES/WGS VCFs through ANNOVAR/InterVar annotation, ACMG-cancer-gene PLP/PTV variant extraction, allele-frequency filtering, and per-cohort carrier-frequency summaries. The pipeline is designed to run on an HPC cluster using LSF (Load Sharing Facility) job scheduling.

---

## Overview

The pipeline is orchestrated by [`pipeline.py`](pipeline.py), which submits each numbered script as an LSF job with `bsub`, chaining stages so that each job only starts after the previous one completes (`bsub -w "done(<prev_job_id>)"`). Stages flow linearly from raw variant annotation through filtering to carrier frequency analysis.

---

## Key Technologies

| Technology | Role |
|---|---|
| **Python** (pandas, numpy) | Summary generation, carrier frequency calculation, VCF filtering |
| **R** | Annotation merging, PLP/PTV variant extraction (ACMG/AMP guidelines) |
| **Bash** | Shell wrappers for each pipeline step and cluster job submission |
| **LSF (`bsub`)** | HPC job scheduling with sequential dependency chaining |
| **AnnoVar / InterVar** | Variant annotation and clinical significance classification |
| **VCF format** | Standard genomics file format for storing genetic variants |
| **pytest** | Python unit testing |

---

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

Each pipeline stage has a `.sh` wrapper (for LSF submission) and a corresponding `.R` or `.py` file containing the core logic.

---

## Prerequisites

- Python 3.10+ with `pandas`, `numpy` (`pip install -r requirements.txt`)
- R with `readr`, `dplyr`, `readxl`
- `bcftools`, `bgzip`
- ANNOVAR (with the `humandb/` databases referenced in `s1_run_intjob.sh`)
- InterVar 2.2.1
- LSF (the wrappers use `bsub`)

---

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

---

## Pipeline Stages

### Step 1 — Preprocessing: Variant Annotation

| Script | Description |
|---|---|
| `scripts/preprocessing/s1_run_intjob.sh` | Runs AnnoVar/InterVar to annotate the initial variant callset. |
| `scripts/preprocessing/s2_Merge_annotation.R` | Joins ANNOVAR + InterVar multianno tables on the variant key (Chr, Start, End, Ref, Alt) using `dplyr::full_join` — no fragile string-paste matching. |

---

### Step 2 — Feature Extraction

| Script | Description |
|---|---|
| `scripts/feature_extraction/s3_Extract_PLP_PTV_variants.R` | Extracts PLP (pathogenic/likely pathogenic) and PTV (protein-truncating) variants on ACMG cancer genes, applying ACMG/AMP classification guidelines. |

---

### Steps 3–6 — Filtering

| Script | Description |
|---|---|
| `scripts/filtering/s4_Filtering.PLP_s1.sh` | First-pass position-level filter on PLP variants. |
| `scripts/filtering/s4_Filtering.PLP_s2.sh` | Second-pass filter on PLP variants by ref/alt allele via `utils/General_2nd_filterVCF.py`. |
| `scripts/filtering/s5_Retain_rareSite_inVCF_filterbyAF.sh` | Retains rare sites (AF < 0.05%) in per-chromosome VCF files. Submit as a **job array `[1-24]`**; each task processes one chromosome (1–22, X, Y). |
| `scripts/filtering/s5b_Concat_filtered_chroms.sh` | Concatenates, sorts, and indexes the per-chromosome outputs from s5. Submit **after** the s5 array finishes. |
| `scripts/filtering/s6_filterExomesByVariants_PTV.sh` | Filters exome VCFs down to sites carrying PTV variants. |
| `scripts/filtering/s7_Getting_rare_PTV.sh` | Extracts the final set of rare PTVs. |

> **Note:** `scripts/utils/General_2nd_filterVCF.py` is a shared VCF filtering utility. It reads a variant table produced by ANNOVAR, normalizes indel representations, and writes a filtered VCF.

---

### Steps 7–8 — Summary & Carrier Frequency Analysis

| Script | Description |
|---|---|
| `scripts/summary/s8_Generate_summary_df.py` | Reads the filtered PLP and PTV VCFs, annotates variants with gene names, identifies carriers per patient, and writes per-tag (`PLP`, `PTV`, `PLP & PTV`) summary TSV files. |
| `scripts/summary/s9_Cal_carrier_Freq.py` | Calculates carrier frequencies from the summary table at four levels: whole-cohort by group, gene × group, ancestry × group, and ancestry × gene × group. |

---

## Running the Pipeline

```bash
python pipeline.py
```

The orchestrator submits each stage with `bsub` and chains them with `-w "done(<prev>)"`, so the cluster runs them in order. Each `submit_job` call returns the LSF job-id; the next stage waits on it.

---

## Testing

```bash
pip install -r requirements-dev.txt
pytest tests/
```

| Test file | What it covers |
|---|---|
| `test_pipeline.py` | `bsub` command construction and LSF job-ID chaining logic |
| `test_carrier_detection.py` | Carrier genotype detection logic |
| `test_filter_vcf_roundtrip.py` | VCF filtering round-trip correctness |
| `test_general_2nd_filter.py` | `General_2nd_filterVCF.py` utility |
| `test_shell_scripts.py` | Shell script smoke tests |
| `test_annotate_vcf_with_gene.py` | Parity tests for the vectorized gene-annotation merge |
| `test_config.py` | Config defaults and env overrides agree between Python and shell |
| `test_r_scripts.py` | No hardcoded cohort paths in R; s2 uses join keys; s3 uses post-rename column names |
| `test_shell_scripts_use_config.py` | Every wrapper sources `config.sh` and derives `REPO_ROOT` from `BASH_SOURCE` |
