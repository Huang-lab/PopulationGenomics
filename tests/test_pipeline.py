"""Tests for pipeline.py: bsub command construction, job-id parsing, and
end-to-end dependency chaining (with a fake runner)."""

import subprocess
from dataclasses import dataclass

import pytest

from conftest import load_module

mod = load_module("pipeline.py", "pipeline_under_test")


class TestBuildBsubCommand:
    def test_unchained(self):
        # Critical: must use a single-string command (shell=True with a list
        # silently drops everything after the first element).
        assert mod.build_bsub_command("scripts/s1.sh") == "bsub < scripts/s1.sh"

    def test_chained(self):
        cmd = mod.build_bsub_command("scripts/s2.sh", after=42)
        assert cmd == 'bsub -w "done(42)" < scripts/s2.sh'

    def test_quotes_paths_with_spaces(self):
        cmd = mod.build_bsub_command("scripts/has space.sh")
        # Must round-trip through a shell without splitting the path.
        assert "'scripts/has space.sh'" in cmd


class TestParseJobId:
    def test_parses_typical_lsf_output(self):
        out = "Job <12345> is submitted to queue <premium>.\n"
        assert mod.parse_job_id(out) == 12345

    def test_raises_on_garbage(self):
        with pytest.raises(RuntimeError):
            mod.parse_job_id("nope")


@dataclass
class _FakeResult:
    returncode: int
    stdout: str
    stderr: str = ""


class FakeRunner:
    """Records every bsub invocation and returns a sequential job-id."""

    def __init__(self):
        self.calls: list[str] = []
        self._next_id = 1000

    def __call__(self, cmd, shell=False, capture_output=False, text=False):
        assert shell is True, "must use shell=True so '<' redirection works"
        assert isinstance(cmd, str), "command must be a single shell string"
        self.calls.append(cmd)
        self._next_id += 1
        return _FakeResult(
            returncode=0,
            stdout=f"Job <{self._next_id}> is submitted to queue <premium>.\n",
        )


class TestMainChaining:
    def test_chains_each_stage_to_the_previous_jobid(self):
        runner = FakeRunner()
        scripts = ["a.sh", "b.sh", "c.sh"]
        ids = mod.main(scripts=scripts, runner=runner)

        assert ids == [1001, 1002, 1003]
        assert runner.calls == [
            "bsub < a.sh",
            'bsub -w "done(1001)" < b.sh',
            'bsub -w "done(1002)" < c.sh',
        ]

    def test_runner_failure_aborts(self):
        def bad_runner(cmd, **kwargs):
            return _FakeResult(returncode=1, stdout="", stderr="boom")

        with pytest.raises(RuntimeError, match="bsub failed"):
            mod.main(scripts=["a.sh"], runner=bad_runner)


def test_old_buggy_form_would_have_failed():
    """Sanity check: confirm the original ['bsub','<',path] + shell=True form
    really does drop arguments. This guards against ever reintroducing it.
    """
    # /bin/sh -c only sees 'bsub'; the rest become positional args to /bin/sh.
    # We invoke a harmless shell instead of bsub to confirm the behavior.
    result = subprocess.run(
        ["printf", "first=%s second=%s\\n", "<", "path.sh"],
        shell=True,
        capture_output=True,
        text=True,
    )
    # When shell=True receives a list, only the first element is the command.
    # `printf` runs with no args (prints nothing); '<' and 'path.sh' don't reach it.
    assert result.stdout == ""
