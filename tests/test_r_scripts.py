"""Static checks on R scripts.

We can't execute R in this environment, but we can sanity-check that:
  - paths come from env vars (set by the wrapper shell scripts), not
    from hardcoded /sc/arion/... strings
  - the rename-then-reference dance in s3 is internally consistent (the
    original used dot names after renaming to underscores, which silently
    produced an empty truncations file)
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
S2 = REPO / "scripts/preprocessing/s2_Merge_annotation.R"
S3 = REPO / "scripts/feature_extraction/s3_Extract_PLP_PTV_variants.R"


def test_no_hardcoded_project_paths_in_r():
    offenders = []
    for r in (S2, S3):
        if "/sc/arion/projects/rg_huangk06" in r.read_text():
            offenders.append(str(r))
    assert not offenders, "hardcoded paths in R:\n" + "\n".join(offenders)


def _strip_r_comments(src: str) -> str:
    """Drop everything from `#` to end-of-line on each line."""
    return "\n".join(re.sub(r"#.*$", "", ln) for ln in src.splitlines())


def test_s2_uses_proper_join_not_string_paste():
    src = _strip_r_comments(S2.read_text())
    # paste(...) inside match(...) was the fragile pattern. A real join
    # (full_join / inner_join / merge by =) is required.
    assert "match(paste" not in src
    assert any(k in src for k in ("full_join", "inner_join", "merge("))


def test_s3_does_not_reference_renamed_columns_with_old_names():
    """After s3 renames `ExonicFunc.refGene` -> `ExonicFunc_refGene` and
    `Func.refGene` -> `Func_refGene` on `ann_subset`, it must not later
    reference the old dot-form on `ann_subset` or `ann_tru`. (df$ExonicFunc.refGene
    on a renamed df is NULL in R, which silently empties downstream filters.)
    """
    src = S3.read_text()
    # Find the rename and everything after it.
    rename_idx = src.find("ExonicFunc_refGene")
    assert rename_idx >= 0, "expected the renamed column form in s3"
    tail = src[rename_idx:]

    # Forbid `ann_subset$ExonicFunc.refGene` and `ann_tru$ExonicFunc.refGene`
    # (and their Func.refGene counterparts) anywhere after the rename.
    forbidden = re.compile(r"(ann_subset|ann_tru)\$(ExonicFunc|Func)\.refGene")
    matches = forbidden.findall(tail)
    assert not matches, f"references to pre-rename column names: {matches}"
