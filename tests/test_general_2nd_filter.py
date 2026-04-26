"""Tests for scripts/utils/General_2nd_filterVCF.py.

Specifically nails down ANNOVAR-style normalization of REF/ALT, which is
used to match VCF rows against ANNOVAR-derived variant tables.
"""

from conftest import load_module

mod = load_module("scripts/utils/General_2nd_filterVCF.py", "general_2nd_filter")


class TestTransformForAnnovar:
    def test_snv_passthrough(self):
        assert mod.transform_for_annovarV2("A", "G") == ("A", "G")

    def test_simple_insertion(self):
        # VCF: REF=A ALT=ATG  ->  ANNOVAR insertion: ref="-", alt="TG"
        assert mod.transform_for_annovarV2("A", "ATG") == ("-", "TG")

    def test_simple_deletion(self):
        # VCF: REF=ATG ALT=A  ->  ANNOVAR deletion: ref="TG", alt="-"
        assert mod.transform_for_annovarV2("ATG", "A") == ("TG", "-")

    def test_single_base_deletion(self):
        # VCF: REF=AT ALT=A  ->  ANNOVAR: ref="T", alt="-"
        assert mod.transform_for_annovarV2("AT", "A") == ("T", "-")

    def test_spanning_deletion_star(self):
        # VCF '*' ALT means the position is deleted by an upstream allele.
        # ANNOVAR doesn't represent these; returning input unchanged is fine,
        # but it must NOT collide with the regular deletion form.
        ref_out, alt_out = mod.transform_for_annovarV2("ATG", "*")
        assert (ref_out, alt_out) != ("TG", "-")
