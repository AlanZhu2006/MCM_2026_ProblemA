#!/usr/bin/env python3
"""Notebook path resolver for trajectory CSVs (A_MCM_A)."""

from __future__ import annotations

import os
from pathlib import Path


def resolve_csv_path() -> str:
    # 1) Environment variable override
    env_path = os.environ.get("A_MCM_A_CSV_PATH")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return str(p)

    # 2) Default repository-relative path from notebook location
    root = Path(__file__).resolve().parents[2]  # go up to repo root
    default_path = root / "A_MCM_A" / "output" / "trajectory_demo.csv"
    if default_path.exists():
        return str(default_path)

    # 3) Fallback to a common relative path (best effort)
    alt_path = Path(root) / "output" / "trajectory_demo.csv"
    return str(alt_path)


if __name__ == "__main__":
    print(resolve_csv_path())
