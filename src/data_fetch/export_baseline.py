"""Export the normal baseline (currently in CSV) to .txt and .jsonl formats.

Input precedence:
  1) data/normal_baseline.csv (preferred)
  2) data/kaggle_phishing.csv (filter label=='clean')
  3) data/sample_dataset.csv (filter label=='clean')

Outputs:
  data/normal_baseline.txt    (one message per line)
  data/normal_baseline.jsonl  ({"text": "..."} per line)

Usage:
  python -m src.data_fetch.export_baseline
"""
from __future__ import annotations

import os
from pathlib import Path
import sys
import pandas as pd

CSV_BASELINE = Path('data') / 'normal_baseline.csv'
KAGGLE = Path('data') / 'kaggle_phishing.csv'
SAMPLE = Path('data') / 'sample_dataset.csv'
TXT_OUT = Path('data') / 'normal_baseline.txt'
JSONL_OUT = Path('data') / 'normal_baseline.jsonl'


def load_texts() -> list[str]:
    if CSV_BASELINE.exists():
        df = pd.read_csv(CSV_BASELINE)
        if 'text' in df.columns:
            return [str(t).strip() for t in df['text'] if str(t).strip()]
    for candidate in (KAGGLE, SAMPLE):
        if candidate.exists():
            df = pd.read_csv(candidate)
            if {'text','label'}.issubset(df.columns):
                clean_df = df[df['label'].str.lower() == 'clean']
                return [str(t).strip() for t in clean_df['text'] if str(t).strip()]
    return []


def export(texts: list[str]) -> int:
    if not texts:
        print('No baseline texts found. Build one first (build_normal_baseline.py).', file=sys.stderr)
        return 1
    TXT_OUT.parent.mkdir(parents=True, exist_ok=True)
    with TXT_OUT.open('w', encoding='utf-8') as f:
        for t in texts:
            f.write(t.replace('\n', ' ') + '\n')
    with JSONL_OUT.open('w', encoding='utf-8') as f:
        for t in texts:
            f.write('{"text": ' + pd.io.json.dumps(t) + '}\n')
    print(f'Wrote {TXT_OUT} and {JSONL_OUT} with {len(texts)} lines.')
    return 0


def main() -> int:
    texts = load_texts()
    return export(texts)


if __name__ == '__main__':
    raise SystemExit(main())
