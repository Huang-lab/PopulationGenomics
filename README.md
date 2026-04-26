# PopulationGenomics

A bioinformatics pipeline for population-scale genomics research. It identifies and analyzes pathogenic/likely pathogenic (PLP) and protein-truncating variants (PTVs) in ACMG cancer genes across a large patient cohort (Mount Sinai BioMe Cohort II). The pipeline is designed to run on an HPC cluster using LSF (Load Sharing Facility) job scheduling.

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

## Repository Structure

```
PopulationGenomics/
├── pipeline.py                          # Orchestrator: chains all stages as LSF jobs
├── requirements-dev.txt                 # Python dev dependencies (pandas, numpy, pytest)
├── scripts/
│   ├── preprocessing/                   # Steps 1–2: Annotation
│   ├── feature_extraction/              # Step 3:  Variant extraction
│   ├── filtering/                       # Steps 4–7: Multi-stage filtering
│   ├── summary/                         # Steps 8–9: Analysis outputs
│   └── utils/                           # Shared utilities
└── tests/                               # Python unit tests
```

Each pipeline stage has a `.sh` wrapper (for LSF submission) and a corresponding `.R` or `.py` file containing the core logic.

---

## Pipeline Stages

### Step 1 — Preprocessing: Variant Annotation

| Script | Description |
|---|---|
| `scripts/preprocessing/s1_run_intjob.sh` | Runs AnnoVar/InterVar to annotate the initial variant callset for the BioMe Cohort II. |
| `scripts/preprocessing/s2_Merge_annotation.R` | Merges the per-sample AnnoVar/InterVar annotation outputs into a single table. |

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
| `scripts/filtering/s4_Filtering.PLP_s2.sh` | Second-pass filter on PLP variants by ref/alt allele. |
| `scripts/filtering/s5_Retain_rareSite_inVCF_filterbyAF.sh` | Retains rare sites (AF < 0.05%) in per-chromosome VCF files. Submit as a **job array `[1-24]`**; each task processes one chromosome (1–22, X, Y). |
| `scripts/filtering/s5b_Concat_filtered_chroms.sh` | Concatenates, sorts, and indexes the per-chromosome outputs from s5. Submit **after** the s5 array finishes. |
| `scripts/filtering/s6_filterExomesByVariants_PTV.sh` | Filters exome VCFs down to sites carrying PTV variants. |
| `scripts/filtering/s7_Getting_rare_PTV.sh` | Extracts the final set of rare PTVs. |

> **Note:** `scripts/utils/General_2nd_filterVCF.py` is a shared VCF filtering utility used by the filtering steps. It reads a variant table produced by ANNOVAR, normalizes indel representations (e.g. converting VCF-style to ANNOVAR-style), and writes a filtered VCF.

---

### Steps 7–8 — Summary & Carrier Frequency Analysis

| Script | Description |
|---|---|
| `scripts/summary/s8_Generate_summary_df.py` | Reads the filtered PLP and PTV VCFs, annotates variants with gene names, identifies carriers per patient, and writes per-tag (`PLP`, `PTV`, `PLP & PTV`) summary TSV files. |
| `scripts/summary/s9_Cal_carrier_Freq.py` | Calculates carrier frequencies from the summary table at four levels: whole-cohort by group, gene × group, ancestry × group, and ancestry × gene × group. |

---

## Running the Pipeline

Submit all stages as a chain of dependent LSF jobs with:

```bash
python pipeline.py
```

This queues all scripts in order; each job waits for the previous one to complete before starting.

---

## Tests

Unit tests cover the Python components:

```bash
pytest tests/
```

| Test file | What it covers |
|---|---|
| `test_pipeline.py` | `bsub` command construction and LSF job-ID chaining logic |
| `test_carrier_detection.py` | Carrier genotype detection logic |
| `test_filter_vcf_roundtrip.py` | VCF filtering round-trip correctness |
| `test_general_2nd_filter.py` | `General_2nd_filterVCF.py` utility |
| `test_shell_scripts.py` | Shell script smoke tests |
