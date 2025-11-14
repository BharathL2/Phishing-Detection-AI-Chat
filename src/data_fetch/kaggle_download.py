"""Kaggle dataset downloader for phishing/spam email datasets.

Usage (PowerShell):
  python -m src.data_fetch.kaggle_download --dataset owner/dataset-slug [--dest data/raw] [--unzip]

Requirements:
  - pip install kaggle
  - Place kaggle.json at %USERPROFILE%\.kaggle\kaggle.json or set KAGGLE_USERNAME/KAGGLE_KEY env vars.

This script intentionally does not pin to a specific dataset. Pass the slug explicitly so you
can use any Kaggle dataset that fits your needs.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def ensure_kaggle_available():
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi  # type: ignore
        return KaggleApi
    except Exception as e:
        print("ERROR: The 'kaggle' package is not installed.", file=sys.stderr)
        print("Install it with: pip install kaggle", file=sys.stderr)
        raise


def download_dataset(dataset_slug: str, dest: Path, unzip: bool = True, force: bool = False) -> Path:
    KaggleApi = ensure_kaggle_available()
    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as e:
        print("ERROR: Kaggle API authentication failed.", file=sys.stderr)
        print("Ensure kaggle.json exists at %USERPROFILE%\\.kaggle\\kaggle.json or set KAGGLE_USERNAME/KAGGLE_KEY.", file=sys.stderr)
        raise

    dest.mkdir(parents=True, exist_ok=True)
    out_dir = dest / dataset_slug.replace('/', '_')
    if out_dir.exists() and any(out_dir.iterdir()) and not force:
        print(f"Destination {out_dir} already has files. Use --force to re-download.")
        return out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {dataset_slug} to {out_dir} (unzip={unzip}) ...")
    api.dataset_download_files(dataset_slug, path=str(out_dir), unzip=unzip, quiet=False)
    print("Download complete.")
    return out_dir


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Download a Kaggle dataset")
    p.add_argument("--dataset", required=True, help="Kaggle dataset slug in form owner/dataset-slug")
    p.add_argument("--dest", default=str(Path('data') / 'raw'), help="Destination root directory (default: data/raw)")
    p.add_argument("--no-unzip", action="store_true", help="Do not unzip the downloaded archive")
    p.add_argument("--force", action="store_true", help="Redownload even if folder has files")
    args = p.parse_args(argv)

    dest = Path(args.dest)
    unzip = not args.no_unzip
    try:
        out_dir = download_dataset(args.dataset, dest=dest, unzip=unzip, force=args.force)
        print(f"Files saved under: {out_dir}")
        return 0
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
