"""Build a normal (clean) baseline CSV for the dynamic unsupervised server.

Reads either data/kaggle_phishing.csv or data/sample_dataset.csv and filters rows
labeled 'clean'. Produces data/normal_baseline.csv with just a single 'text' column.

Usage:
  python -m src.data_fetch.build_normal_baseline
  python -m src.data_fetch.build_normal_baseline --min 50 --max 500

Parameters:
  --min : minimum number of clean samples required (else non-zero exit)
  --max : cap number of samples (random sample if more)
"""
from __future__ import annotations

import argparse
import os
import random
from pathlib import Path
import sys

import pandas as pd

PRIMARY = Path('data') / 'kaggle_phishing.csv'
FALLBACK = Path('data') / 'sample_dataset.csv'
OUT = Path('data') / 'normal_baseline.csv'


def load_source() -> Path:
    return PRIMARY if PRIMARY.exists() else FALLBACK


def build(min_count: int, max_count: int) -> int:
    src = load_source()
    if not src.exists():
        print(f"ERROR: Source dataset not found at {src}", file=sys.stderr)
        return 1
    df = pd.read_csv(src)
    if 'label' not in df.columns or 'text' not in df.columns:
        print("ERROR: Expected columns 'text' and 'label' not found.", file=sys.stderr)
        return 1
    clean_df = df[df['label'].str.lower() == 'clean'].copy()
    clean_df['text'] = clean_df['text'].fillna('').astype(str).str.strip()
    clean_df = clean_df[clean_df['text'] != '']
    if len(clean_df) < min_count:
        print(f"ERROR: Only {len(clean_df)} clean samples (< min {min_count}).")
        return 1
    if len(clean_df) > max_count:
        clean_df = clean_df.sample(n=max_count, random_state=42)
    clean_df[['text']].to_csv(OUT, index=False)
    print(f"Wrote {OUT} with {len(clean_df)} clean baseline samples.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build normal baseline for dynamic server")
    ap.add_argument('--min', type=int, default=30, help='Minimum required clean samples')
    ap.add_argument('--max', type=int, default=200, help='Maximum samples to retain')
    args = ap.parse_args(argv)
    return build(args.min, args.max)


if __name__ == '__main__':
    raise SystemExit(main())
