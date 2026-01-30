#!/usr/bin/env python3
"""CI helper: run demo notebook and export HTML with robust Python selection

Flow:
- Ensure the CSV data exists (via A_MCM_A/demo_run.py).
- Execute the notebook battery_csv_demo.ipynb and export to HTML.
- Attempts to use multiple Python interpreters (to cope with multiple environments).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
NOTEBOOK_PATH = os.path.join(ROOT, "A_MCM_A", "notebooks", "battery_csv_demo.ipynb")
HTML_OUTPUT = os.path.join(ROOT, "A_MCM_A", "notebooks", "battery_csv_demo.html")


def _try_run_nbconvert(
    python_exec: str, notebook_path: str, html_out_path: str, timeout: int
) -> bool:
    cmd = [
        python_exec,
        "-m",
        "nbconvert",
        "--to",
        "html",
        "--execute",
        notebook_path,
        "--output",
        html_out_path,
        f"--ExecutePreprocessor.timeout={timeout}",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            return False
    except Exception as e:
        print(str(e), file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--notebook", default=NOTEBOOK_PATH, help="Notebook to execute")
    parser.add_argument("--html", default=HTML_OUTPUT, help="Output HTML path")
    parser.add_argument(
        "--timeout", type=int, default=600, help="Execution timeout seconds"
    )
    args = parser.parse_args()

    notebook = os.path.abspath(args.notebook)
    html_out = os.path.abspath(args.html)
    timeout = int(args.timeout)

    # Step 1: ensure CSV exists by running the demo script
    demo_script = os.path.join(ROOT, "A_MCM_A", "demo_run.py")
    if os.path.exists(demo_script):
        print(f"Running demo to generate CSV: {demo_script}")
        ret = subprocess.run(
            [sys.executable, demo_script], capture_output=True, text=True
        )
        print(ret.stdout)
        if ret.returncode != 0:
            print(ret.stderr, file=sys.stderr)
            sys.exit(ret.returncode)
    else:
        print("Demo script not found; proceeding to notebook execution.")

    # Step 2: attempt nbconvert using a set of candidate interpreters
    candidates = [sys.executable]
    if os.name == "nt":
        py_path = shutil.which("py")
        if py_path:
            candidates.append(py_path)
        py311 = shutil.which("python3.11")
        if py311:
            candidates.append(py311)
    else:
        py311 = shutil.which("python3.11")
        if py311:
            candidates.append(py311)

    notebook_path = str(notebook)
    html_path = str(html_out)
    success = False
    for candidate in candidates:
        print(f"Trying nbconvert with: {candidate}")
        if _try_run_nbconvert(candidate, notebook_path, html_path, timeout):
            success = True
            break
    if not success:
        print(
            "Failed to export notebook to HTML with available Python interpreters.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"HTML exported to: {html_out}")


if __name__ == "__main__":
    main()
