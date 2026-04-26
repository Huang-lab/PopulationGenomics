"""Static checks for the shell stage scripts.

These don't run the scripts (they need a real LSF cluster, bcftools, real
VCFs, etc.) but they encode invariants that are easy to break.
"""

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = sorted(REPO.glob("scripts/**/*.sh"))


def test_every_shell_script_parses():
    failures = []
    for script in SCRIPTS:
        result = subprocess.run(
            ["bash", "-n", str(script)], capture_output=True, text=True
        )
        if result.returncode != 0:
            failures.append(f"{script}: {result.stderr.strip()}")
    assert not failures, "shell parse errors:\n" + "\n".join(failures)


def test_s5_uses_lsb_jobindex_not_positional_arg():
    """The array job must read its chromosome from $LSB_JOBINDEX, not $1.

    LSF arrays don't pass $1; the original `chromosome=$1` left the variable
    empty in every task, so every task tried to filter the same (empty) path.
    """
    src = (REPO / "scripts/filtering/s5_Retain_rareSite_inVCF_filterbyAF.sh").read_text()
    assert "LSB_JOBINDEX" in src
    assert "chromosome=$1" not in src


def test_s5_finalize_is_a_separate_script():
    """The concat / sort / index step must NOT live inside the array script,
    or it races itself 24x. It has its own dedicated finalize script."""
    array_src = (REPO / "scripts/filtering/s5_Retain_rareSite_inVCF_filterbyAF.sh").read_text()
    assert "bcftools concat" not in array_src
    assert (REPO / "scripts/filtering/s5b_Concat_filtered_chroms.sh").is_file()


def test_no_ssh_inside_lsf_jobs():
    """`ssh some-host` inside a batch script blocks waiting for an interactive
    shell and the rest of the script never runs on the right host."""
    offenders = []
    for script in SCRIPTS:
        text = script.read_text()
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if stripped.startswith("ssh "):
                offenders.append(f"{script}: {stripped}")
    assert not offenders, "ssh inside batch scripts:\n" + "\n".join(offenders)
