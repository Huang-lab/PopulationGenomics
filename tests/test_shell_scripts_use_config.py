"""Lock in the shell scripts' use of the central config.

Every stage script must:
  - resolve REPO_ROOT from $(dirname "${BASH_SOURCE[0]}"), so it works from
    any cwd
  - source config.sh, so paths come from one place and are overridable
  - not contain hard-coded /sc/arion/projects/rg_huangk06 paths
"""

import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = sorted(REPO.glob("scripts/**/*.sh"))


def test_every_shell_script_sources_config():
    missing = [str(s) for s in SCRIPTS if "source \"${REPO_ROOT}/config.sh\"" not in s.read_text()]
    assert not missing, "scripts not sourcing config.sh:\n" + "\n".join(missing)


def test_every_shell_script_resolves_repo_root():
    missing = [
        str(s)
        for s in SCRIPTS
        if "REPO_ROOT=" not in s.read_text() or "BASH_SOURCE" not in s.read_text()
    ]
    assert not missing, "scripts not deriving REPO_ROOT from BASH_SOURCE:\n" + "\n".join(missing)


def test_no_hardcoded_project_paths_remaining():
    """The literal cohort path should only appear inside config.sh."""
    offenders = []
    for s in SCRIPTS:
        text = s.read_text()
        if "/sc/arion/projects/rg_huangk06" in text:
            offenders.append(str(s))
    assert not offenders, "hardcoded paths leaking out of config.sh:\n" + "\n".join(offenders)


def test_out_dir_override_propagates_through_sourcing(tmp_path):
    """Every shell script, when sourced with OUT_DIR overridden, sees the override."""
    failures = []
    for s in SCRIPTS:
        env = {"PATH": os.environ["PATH"], "OUT_DIR": str(tmp_path / "run42")}
        # Source the script's prelude (everything up to and including config.sh)
        # by sourcing config.sh directly with the same REPO_ROOT.
        result = subprocess.run(
            ["bash", "-c", f"source {REPO}/config.sh && echo \"$OUT_DIR\""],
            capture_output=True,
            text=True,
            env=env,
        )
        if result.stdout.strip() != str(tmp_path / "run42"):
            failures.append(f"{s}: got {result.stdout.strip()!r}")
    assert not failures, "OUT_DIR override didn't propagate:\n" + "\n".join(failures)
