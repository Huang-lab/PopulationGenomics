"""End-to-end test: filter_vcf keeps rows whose ANNOVAR-normalized key is in
the variant table, and drops rows that aren't.
"""

from pathlib import Path

from conftest import load_module

mod = load_module("scripts/utils/General_2nd_filterVCF.py", "general_2nd_filter_e2e")


def test_filter_vcf_roundtrip(tmp_path: Path):
    vcf = tmp_path / "in.vcf"
    vcf.write_text(
        "##fileformat=VCFv4.2\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
        # SNV that should be kept (matches the annovar table directly)
        "chr1\t100\t.\tA\tG\t.\t.\t.\n"
        # Deletion: VCF REF=ATG ALT=A -> annovar (TG, -) — must be kept
        "chr1\t200\t.\tATG\tA\t.\t.\t.\n"
        # Insertion: VCF REF=A ALT=ATG -> annovar (-, TG) — must be kept
        "chr1\t300\t.\tA\tATG\t.\t.\t.\n"
        # SNV not in table — must be dropped
        "chr1\t400\t.\tT\tC\t.\t.\t.\n"
    )

    table = tmp_path / "variants.tsv"
    table.write_text(
        "#CHROM\tPOS\tREF\tALT\n"
        "chr1\t100\tA\tG\n"
        "chr1\t200\tTG\t-\n"
        "chr1\t300\t-\tTG\n"
    )

    out = tmp_path / "out.vcf"
    annovar_variants = mod.read_variant_table(str(table))
    mod.filter_vcf(str(vcf), annovar_variants, str(out))

    body = [ln for ln in out.read_text().splitlines() if not ln.startswith("#")]
    positions = [ln.split("\t")[1] for ln in body]
    assert positions == ["100", "200", "300"]
