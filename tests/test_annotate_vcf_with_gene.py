"""Tests for s8.annotate_vcf_with_gene.

Pins down its behavior so we can vectorize the apply(axis=1) hot path
without changing outputs:
- adds a Ref.Gene column populated from the (#CHROM, POS) -> gene dict
- missing keys map to '.'
- Ref.Gene is placed at column index 5 (right after CHROM/POS/ID/REF/ALT)
- the file is written to output_path as TSV without the index
"""

from pathlib import Path

import pandas as pd

from conftest import load_module

mod = load_module(
    "scripts/summary/s8_Generate_summary_df.py",
    "s8_summary_annot",
)


def _toy_vcf_df():
    return pd.DataFrame(
        {
            "#CHROM": ["chr1", "chr1", "chr2"],
            "POS": [100, 200, 300],
            "ID": [".", ".", "."],
            "REF": ["A", "ATG", "C"],
            "ALT": ["G", "A", "T"],
            "QUAL": [".", ".", "."],
            "FILTER": ["PASS", "PASS", "PASS"],
            "INFO": [".", ".", "."],
            "FORMAT": ["GT", "GT", "GT"],
            "S1": ["0/1", "1/1", "0/0"],
        }
    )


def _toy_gene_info():
    return {
        ("chr1", 100): "BRCA1",
        ("chr1", 200): "BRCA2",
        # chr2:300 deliberately missing -> should land as '.'
    }


def test_adds_ref_gene_column_in_position_5(tmp_path: Path):
    df = _toy_vcf_df()
    out_path = tmp_path / "annotated.vcf"

    result = mod.annotate_vcf_with_gene(df.copy(), _toy_gene_info(), str(out_path))

    assert list(result.columns)[5] == "Ref.Gene"
    assert result["Ref.Gene"].tolist() == ["BRCA1", "BRCA2", "."]


def test_other_columns_preserved_in_order(tmp_path: Path):
    df = _toy_vcf_df()
    expected_other = [c for c in df.columns]

    result = mod.annotate_vcf_with_gene(df.copy(), _toy_gene_info(), str(tmp_path / "x.vcf"))

    cols_without_gene = [c for c in result.columns if c != "Ref.Gene"]
    assert cols_without_gene == expected_other


def test_writes_tsv_file(tmp_path: Path):
    df = _toy_vcf_df()
    out_path = tmp_path / "annotated.vcf"

    mod.annotate_vcf_with_gene(df.copy(), _toy_gene_info(), str(out_path))

    written = pd.read_csv(out_path, sep="\t")
    assert "Ref.Gene" in written.columns
    assert list(written.columns)[5] == "Ref.Gene"
    assert written["Ref.Gene"].fillna(".").tolist() == ["BRCA1", "BRCA2", "."]


def test_handles_empty_dataframe(tmp_path: Path):
    df = _toy_vcf_df().iloc[0:0].copy()
    out_path = tmp_path / "empty.vcf"

    result = mod.annotate_vcf_with_gene(df, _toy_gene_info(), str(out_path))

    assert "Ref.Gene" in result.columns
    assert len(result) == 0
    assert list(result.columns)[5] == "Ref.Gene"
