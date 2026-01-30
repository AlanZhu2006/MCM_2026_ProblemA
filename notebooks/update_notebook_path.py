#!/usr/bin/env python3
"""Notebook path updater for battery_csv_demo.ipynb (A_MCM_A).
This helper patches the notebook to use a path-resolving utility for the CSV input.
It performs two edits:
- Injects a code cell at the top to resolve the CSV path via battery_csv_path_utils.resolve_csv_path()
- Rewrites the data-loading cell to read from csv_path directly
"""

from __future__ import annotations

import json
from pathlib import Path

NOTEBOOK_PATH = Path(__file__).resolve().parents[1] / "battery_csv_demo.ipynb"
CSV_PATH_UTIL = (
    Path(__file__).resolve().parents[2]
    / "A_MCM_A"
    / "notebooks"
    / "battery_csv_path_utils.py"
)


def patch_notebook(nb_path: Path) -> None:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Insert a new code cell at index 1 to resolve CSV path
    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from battery_csv_path_utils import resolve_csv_path\n",
            "csv_path = resolve_csv_path()\n",
            "print('CSV path resolved to:', csv_path)\n",
            "import pandas as pd\n",
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "plt.style.use('seaborn-darkgrid')\n",
            '"""%matplotlib inline"""\n',
        ],
    }
    nb["cells"].insert(1, new_cell)

    # Rewrite the data-loading code cell (search for trajectory_demo.csv usage)
    for idx, cell in enumerate(nb["cells"]):
        if cell.get("cell_type") == "code" and any(
            "trajectory_demo.csv" in s for s in cell.get("source", [])
        ):
            cell["source"] = [
                "# Load trajectory CSV (auto-resolved path)\n",
                "df = pd.read_csv(csv_path)\n",
                "print('Loaded', len(df), 'rows')\n",
                "df.head()\n",
            ]
            break

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)


def main():
    patch_notebook(NOTEBOOK_PATH)
    print(f"Patched notebook: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
