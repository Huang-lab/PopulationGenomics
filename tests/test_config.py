"""Tests for the central config (config.py + config.sh)."""

import importlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _reload_config(env_overrides):
    """Reload config.py with the given env overrides applied."""
    sys.modules.pop("config", None)
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    saved = {k: os.environ.get(k) for k in env_overrides}
    try:
        os.environ.update(env_overrides)
        return importlib.import_module("config")
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class TestConfigPython:
    def test_defaults_match_known_layout(self):
        cfg = _reload_config({})
        assert str(cfg.PROJECT_ROOT) == "/sc/arion/projects/rg_huangk06/variants_PLP_BioMe"
        assert str(cfg.DATA_DIR).endswith("/variants_PLP_BioMe/data")
        assert str(cfg.OUT_DIR).endswith("/variants_PLP_BioMe/out")
        assert cfg.AF_THRESHOLD == 0.0005

    def test_env_overrides_propagate(self, tmp_path):
        cfg = _reload_config(
            {
                "OUT_DIR": str(tmp_path / "out"),
                "AF_THRESHOLD": "0.001",
                "INPUT_VCF_BASENAME": "TestCohort",
            }
        )
        assert cfg.OUT_DIR == tmp_path / "out"
        assert cfg.AF_THRESHOLD == 0.001
        assert cfg.INPUT_VCF_BASENAME == "TestCohort"

    def test_stage8_paths_compose_from_out_dir(self, tmp_path):
        cfg = _reload_config({"OUT_DIR": str(tmp_path / "out")})
        paths = cfg.stage8_paths()
        assert paths.plp_vcf == tmp_path / "out" / "s4_2nd_filter_PLP.vcf"
        assert paths.output_dir.parent == tmp_path / "out"


class TestConfigShell:
    def test_defaults_match_python(self):
        result = subprocess.run(
            ["bash", "-c", f"source {REPO}/config.sh && echo \"$OUT_DIR\" \"$AF_THRESHOLD\""],
            capture_output=True,
            text=True,
            env={"PATH": os.environ["PATH"]},
        )
        assert result.returncode == 0, result.stderr
        out_dir, af = result.stdout.strip().split()
        assert out_dir == "/sc/arion/projects/rg_huangk06/variants_PLP_BioMe/out"
        assert af == "0.0005"

    def test_env_overrides_propagate(self, tmp_path):
        env = {
            "PATH": os.environ["PATH"],
            "OUT_DIR": str(tmp_path / "out"),
            "AF_THRESHOLD": "0.001",
        }
        result = subprocess.run(
            ["bash", "-c", f"source {REPO}/config.sh && echo \"$OUT_DIR\" \"$AF_THRESHOLD\""],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, result.stderr
        out_dir, af = result.stdout.strip().split()
        assert out_dir == str(tmp_path / "out")
        assert af == "0.001"
