"""Submit the population-genomics pipeline as a chain of dependent LSF jobs.

Each stage is queued with `bsub < <script>`, and every stage after the
first declares `-w "done(<prev>)"` so the cluster runs them in order.
"""

import re
import shlex
import subprocess
import sys


JOB_ID_RE = re.compile(r"Job <(\d+)> is submitted")


def build_bsub_command(script_path: str, after: int | None = None) -> str:
    """Return the shell string that submits *script_path* via bsub.

    When *after* is given, gate the job on that LSF job-id finishing.
    """
    quoted = shlex.quote(script_path)
    if after is None:
        return f"bsub < {quoted}"
    return f'bsub -w "done({after})" < {quoted}'


def parse_job_id(bsub_stdout: str) -> int:
    match = JOB_ID_RE.search(bsub_stdout)
    if match is None:
        raise RuntimeError(f"could not parse bsub job id from: {bsub_stdout!r}")
    return int(match.group(1))


def submit_job(script_path: str, after: int | None = None, runner=subprocess.run) -> int:
    cmd = build_bsub_command(script_path, after=after)
    result = runner(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"bsub failed for {script_path}: {result.stderr.strip()}"
        )
    job_id = parse_job_id(result.stdout)
    print(f"submitted {script_path} as job {job_id}"
          + (f" (after {after})" if after is not None else ""))
    return job_id


PIPELINE = [
    "scripts/preprocessing/s1_run_intjob.sh",
    "scripts/preprocessing/s2_Merge_annotation.sh",
    "scripts/feature_extraction/s3_Extract_PLP_PTV_variants.sh",
    "scripts/filtering/s4_Filtering.PLP_s1.sh",
    "scripts/filtering/s4_Filtering.PLP_s2.sh",
    "scripts/filtering/s5_Retain_rareSite_inVCF_filterbyAF.sh",
    "scripts/filtering/s5b_Concat_filtered_chroms.sh",
    "scripts/filtering/s6_filterExomesByVariants_PTV.sh",
    "scripts/filtering/s7_Getting_rare_PTV.sh",
    "scripts/summary/s8_Generate_summary_df.sh",
    "scripts/summary/s9_Cal_carrier_Freq.sh",
]


def main(scripts=PIPELINE, runner=subprocess.run) -> list[int]:
    job_ids: list[int] = []
    prev: int | None = None
    for script in scripts:
        prev = submit_job(script, after=prev, runner=runner)
        job_ids.append(prev)
    return job_ids


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
