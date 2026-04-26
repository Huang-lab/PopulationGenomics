"""Tests for is_carrier in s8_Generate_summary_df.

Pinning down the bug where the original implementation only matched the
literal substring '0/1', missing hom-alt, phased, and reversed genotypes.
"""

import pytest

from conftest import load_module

mod = load_module(
    "scripts/summary/s8_Generate_summary_df.py",
    "s8_summary",
)


@pytest.mark.parametrize(
    "gt",
    [
        "0/1",
        "1/0",
        "1/1",
        "0|1",
        "1|0",
        "1|1",
        "0/2",  # multi-allelic, alt index 2
        "1/2",
        "0/1:30:0,30",  # GT plus AD/DP fields
        "1|1:50:0,50",
    ],
)
def test_is_carrier_true(gt):
    assert mod.is_carrier(gt) == 1


@pytest.mark.parametrize(
    "gt",
    [
        "0/0",
        "0|0",
        "./.",
        ".",
        "",
        None,
        "0/0:30:30,0",
    ],
)
def test_is_carrier_false(gt):
    assert mod.is_carrier(gt) == 0


def test_is_carrier_does_not_substring_match_0_slash_10():
    # '0/10' is not a real VCF GT (allele indices >9 are rare but legal).
    # Critically, it should NOT be flagged just because '0/1' is a substring.
    assert mod.is_carrier("0/10") == 1  # actual carrier (alt allele 10)
    # but '10/0' should also be a carrier, not driven by substring '/0'
    assert mod.is_carrier("10/0") == 1
