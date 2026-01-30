#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname "$0")"/.. && pwd)
ROOT=$(cd "$SCRIPT_DIR" && cd .. && pwd)
echo "Root: $ROOT"

# Step 1: Generate CSV via demo_run.py
python "$ROOT/A_MCM_A/demo_run.py"

# Step 2: Export notebook to HTML, executing it with timeout
NOTEBOOK="$ROOT/A_MCM_A/notebooks/battery_csv_demo.ipynb"
OUTPUT_HTML="$ROOT/A_MCM_A/notebooks/battery_csv_demo.html"
python -m nbconvert --to html --execute "$NOTEBOOK" --output "$OUTPUT_HTML" --ExecutePreprocessor.timeout=600
echo "HTML exported to: $OUTPUT_HTML"
