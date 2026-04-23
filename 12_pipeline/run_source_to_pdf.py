#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run the end-to-end pipeline from 12_pipeline/source.tex to final PDF.

Usage:
    python 12_pipeline/run_source_to_pdf.py 03
    python 12_pipeline/run_source_to_pdf.py conic
    python 12_pipeline/run_source_to_pdf.py 03_conic --dry-run
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

NEW_ID_PATTERN = re.compile(r"^NEW_ID=([A-Za-z]\d{3})\s*$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "One-click flow: source.tex -> create input case -> run pipeline -> "
            "publish -> fix math punctuation -> build PDF."
        )
    )
    parser.add_argument(
        "module_selector",
        help="Module selector for create_next_input_case.py, e.g. 03 / conic / 03_conic",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned commands only; do not execute any step.",
    )
    parser.add_argument(
        "--python-exe",
        default=sys.executable,
        help="Python executable path used to run sub-scripts. Default: current interpreter.",
    )
    return parser.parse_args()


def quoted_command(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def ensure_source_tex_ready(source_tex: Path) -> None:
    if not source_tex.is_file():
        raise FileNotFoundError(f"Missing source file: {source_tex}")
    if source_tex.stat().st_size == 0:
        raise ValueError(f"source.tex is empty: {source_tex}")


def run_command(label: str, cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    print(f"[start] {label}")
    print(f"[cmd] {quoted_command(cmd)}")
    t0 = time.perf_counter()
    completed = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
    )
    elapsed = time.perf_counter() - t0

    if completed.returncode != 0:
        print(f"[fail] {label} ({elapsed:.2f}s)")
        if completed.stdout.strip():
            print("[stdout]")
            print(completed.stdout.rstrip())
        if completed.stderr.strip():
            print("[stderr]")
            print(completed.stderr.rstrip())
        raise RuntimeError(f"{label} failed with exit code {completed.returncode}")

    print(f"[ok]   {label} ({elapsed:.2f}s)")
    return completed


def parse_new_id(stdout: str) -> str:
    match = NEW_ID_PATTERN.search(stdout)
    if not match:
        raise ValueError("Cannot parse NEW_ID from create_next_input_case.py output.")
    return match.group(1).upper()


def run_flow(args: argparse.Namespace) -> int:
    script_path = Path(__file__).resolve()
    pipeline_dir = script_path.parent
    project_root = pipeline_dir.parent
    source_tex = pipeline_dir / "source.tex"

    ensure_source_tex_ready(source_tex)

    python_exe = str(Path(args.python_exe))
    create_script = pipeline_dir / "create_next_input_case.py"
    run_script = pipeline_dir / "run_pipeline.py"
    publish_script = pipeline_dir / "publish_pipeline_output.py"
    fix_script = project_root / "scripts" / "fix_math_punctuation.py"
    build_pdf_script = project_root / "scripts" / "build_conclusion_pdfs.py"

    if args.dry_run:
        planned_id = "<NEW_ID_FROM_STEP1>"
        plan = [
            ("Step 1/5 create next input case", [python_exe, str(create_script), args.module_selector]),
            ("Step 2/5 run pipeline", [python_exe, str(run_script), planned_id]),
            ("Step 3/5 publish output", [python_exe, str(publish_script), planned_id]),
            ("Step 4/5 fix math punctuation", [python_exe, str(fix_script), planned_id]),
            (
                "Step 5/5 build PDF",
                [python_exe, str(build_pdf_script), planned_id, "--pdf-name-mode", "id"],
            ),
        ]
        print(f"[info] Project root: {project_root}")
        print(f"[info] source.tex: {source_tex}")
        print("[info] Mode: dry-run")
        for label, cmd in plan:
            print(f"[plan] {label}")
            print(f"       {quoted_command(cmd)}")
        return 0

    print(f"[info] Project root: {project_root}")
    print(f"[info] source.tex: {source_tex}")
    print("[info] Mode: execute")

    create_cmd = [python_exe, str(create_script), args.module_selector]
    create_result = run_command("Step 1/5 create next input case", create_cmd, project_root)
    if create_result.stdout.strip():
        print("[stdout]")
        print(create_result.stdout.rstrip())

    new_id = parse_new_id(create_result.stdout)
    print(f"[info] Parsed NEW_ID={new_id}")

    run_command(
        "Step 2/5 run pipeline",
        [python_exe, str(run_script), new_id],
        project_root,
    )
    run_command(
        "Step 3/5 publish output",
        [python_exe, str(publish_script), new_id],
        project_root,
    )
    run_command(
        "Step 4/5 fix math punctuation",
        [python_exe, str(fix_script), new_id],
        project_root,
    )
    run_command(
        "Step 5/5 build PDF",
        [python_exe, str(build_pdf_script), new_id, "--pdf-name-mode", "id"],
        project_root,
    )

    pdf_path = project_root / "build" / "conclusion_pdfs" / f"{new_id}.pdf"
    print(f"NEW_ID={new_id}")
    print(f"PDF_EXPECTED={pdf_path}")
    if pdf_path.is_file():
        print(f"PDF_READY={pdf_path}")
    else:
        print(f"[warn] PDF file not found yet: {pdf_path}")

    return 0


def main() -> int:
    args = parse_args()
    try:
        return run_flow(args)
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"[error] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

