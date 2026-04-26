"""Single source of truth for paths and tunables.

Every value can be overridden by an env var of the same name, so the
pipeline runs against a different cohort or output directory by setting
e.g. `OUT_DIR=/path/to/run42 python pipeline.py` -- no code changes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _path(name: str, default: str) -> Path:
    return Path(_env(name, default))


REPO_ROOT = Path(__file__).resolve().parent

# Top-level cohort directories. Defaults match the BioMe Sema4 layout.
PROJECT_ROOT = _path("PROJECT_ROOT", "/sc/arion/projects/rg_huangk06/variants_PLP_BioMe")
DATA_DIR = _path("DATA_DIR", str(PROJECT_ROOT / "data"))
OUT_DIR = _path("OUT_DIR", str(PROJECT_ROOT / "out"))
METADATA_DIR = _path("METADATA_DIR", str(PROJECT_ROOT / "metadata"))
CHROM_DIR = _path("CHROM_DIR", str(DATA_DIR / "chromosome"))
INTERVAR_DIR = _path("INTERVAR_DIR", str(PROJECT_ROOT / "tools" / "InterVar-2.2.1"))
TMPDIR = _path("TMPDIR", str(REPO_ROOT / "scripts" / "tmp"))

# External resources.
ACMG_XLSX = _path(
    "ACMG_XLSX",
    "/sc/arion/projects/rg_huangk06/variantDisease/data/cancer/ACMG_SF_v32_supp.xlsx",
)

# Cohort-specific knobs.
INPUT_VCF_BASENAME = _env("INPUT_VCF_BASENAME", "BioMe_Sema4_WES")
PATIENT_INFO_NAME = _env("PATIENT_INFO_NAME", "Sema4_HX_WXS_Newgroups.tsv")
AF_THRESHOLD = float(_env("AF_THRESHOLD", "0.0005"))


@dataclass(frozen=True)
class Stage8Paths:
    plp_vcf: Path
    ptv_vcf: Path
    plp_gene_info: Path
    ptv_gene_info: Path
    patient_info: Path
    output_dir: Path


def stage8_paths() -> Stage8Paths:
    return Stage8Paths(
        plp_vcf=OUT_DIR / "s4_2nd_filter_PLP.vcf",
        ptv_vcf=OUT_DIR / "S7_Filtered_ACMG32_truncations005" / "ACMG32_AF005_PTV_2ndfiltered.vcf",
        plp_gene_info=OUT_DIR / "s3_ACMG32_cancer_gene.predis.plp.txt",
        ptv_gene_info=OUT_DIR / "s3_ACMG32_cancer_gene_truncations.txt",
        patient_info=METADATA_DIR / PATIENT_INFO_NAME,
        output_dir=OUT_DIR / _env("STAGE8_SUBDIR", "summary"),
    )
