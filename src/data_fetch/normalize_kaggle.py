"""Normalize downloaded Kaggle CSVs into data/kaggle_phishing.csv

Heuristics:
- Text column candidates: text, email text, body, content, message (fallback: subject)
- Label column candidates: label, phishing, is_phishing, class, target
- Label mapping: phishing/spam/malicious/1/true/yes -> phishing; ham/legitimate/clean/0/false/no -> clean

Usage:
  python -m src.data_fetch.normalize_kaggle --root data/raw --out data/kaggle_phishing.csv
"""
from __future__ import annotations

import argparse
import glob
import os
from pathlib import Path
from typing import List, Dict

import pandas as pd


TEXT_CANDIDATES = {"text", "email text", "body", "content", "message"}
LABEL_CANDIDATES = {"label", "phishing", "is_phishing", "class", "target"}


def normalize(root: Path, out_path: Path) -> int:
    csv_paths = glob.glob(str(root / "**" / "*.csv"), recursive=True)
    rows: List[Dict[str, str]] = []
    for p in csv_paths:
        try:
            df = pd.read_csv(p, encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if df.empty:
            continue
        cols_lower = {c.lower(): c for c in df.columns}
        text_col = next((cols_lower[c] for c in cols_lower if c in TEXT_CANDIDATES), None)
        subj_col = cols_lower.get("subject")
        label_col = next((cols_lower[c] for c in cols_lower if c in LABEL_CANDIDATES), None)
        if not text_col and subj_col:
            text_col = subj_col
        if not text_col or not label_col:
            continue
        for _, r in df.iterrows():
            raw_text = str(r.get(text_col, "")).strip()
            if subj_col:
                raw_text = (str(r.get(subj_col, "")).strip() + " " + raw_text).strip()
            if not raw_text:
                continue
            raw_label = str(r.get(label_col, "")).strip().lower()
            if raw_label in ("phishing", "spam", "malicious", "1", "true", "yes"):
                mapped = "phishing"
            elif raw_label in ("ham", "legitimate", "clean", "0", "false", "no"):
                mapped = "clean"
            else:
                continue
            rows.append({"text": raw_text, "label": mapped})
    if not rows:
        print("No rows collected. Check column heuristics or dataset contents.")
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).drop_duplicates().to_csv(out_path, index=False)
    print(f"Wrote {out_path} with {len(rows)} rows (pre-dedup).")
    return len(rows)


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Normalize Kaggle CSVs into text,label format")
    ap.add_argument("--root", default=str(Path("data") / "raw"), help="Root folder containing downloaded CSVs")
    ap.add_argument("--out", default=str(Path("data") / "kaggle_phishing.csv"), help="Output CSV path")
    args = ap.parse_args(argv)

    count = normalize(Path(args.root), Path(args.out))
    return 0 if count > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
