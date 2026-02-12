"""Zillow Research data acquisition: ZHVI and ZORI by ZIP."""

from __future__ import annotations

import argparse
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd

from ._utils import (
    RAW_DIR,
    ensure_dirs,
    timestamped_filename,
    write_ingest_log,
    write_sources_md,
    dataframe_ingest_stats,
)
from ._http import get_with_retries

# Zillow download URLs — may change; check https://www.zillow.com/research/data/
# Override via env: ZILLOW_ZHVI_URL, ZILLOW_ZORI_URL
ZILLOW_BASE = "https://www.zillow.com/research/data"
# Historical URLs (as of 2024; verify before use)
DEFAULT_ZHVI_URL = "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
DEFAULT_ZORI_URL = "https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_sm_month.csv"

INBOX_DIR = RAW_DIR / "zillow" / "inbox"
OUTPUT_DIR = RAW_DIR / "zillow"


def _get_download_url(dataset: str) -> str:
    import os

    if dataset == "zhvi":
        return os.environ.get("ZILLOW_ZHVI_URL", DEFAULT_ZHVI_URL)
    if dataset == "zori":
        return os.environ.get("ZILLOW_ZORI_URL", DEFAULT_ZORI_URL)
    raise ValueError(f"Unknown dataset: {dataset}. Use 'zhvi' or 'zori'.")


def run_inbox(dataset: str) -> Path | None:
    """Ingest from inbox: data/raw/zillow/inbox/. Timestamp and log."""
    ensure_dirs(INBOX_DIR, OUTPUT_DIR)
    # Look for any CSV that might be the dataset
    pattern = "*.csv"
    inbox_files = list(INBOX_DIR.glob(pattern))
    if not inbox_files:
        print(f"No CSV files found in {INBOX_DIR}. Place Zillow {dataset.upper()} CSV there.")
        return None
    # Use the most recently modified
    latest = max(inbox_files, key=lambda p: p.stat().st_mtime)
    df = pd.read_csv(latest)
    out_name = timestamped_filename(f"zillow_{dataset}", "csv")
    out_path = OUTPUT_DIR / out_name
    df.to_csv(out_path, index=False)
    _log_ingest(df, out_path, dataset, "inbox", {"inbox_file": str(latest)})
    _update_sources(dataset, "inbox", {"inbox_file": str(latest)})
    print(f"Ingested {len(df)} rows from {latest.name} -> {out_path}")
    # Optionally move/remove inbox file to avoid re-ingestion
    # Keeping it for now; user can delete manually
    return out_path


def run_download(dataset: str) -> Path | None:
    """Download from Zillow URL. URL may change — check Zillow Research data page."""
    url = _get_download_url(dataset)
    ensure_dirs(OUTPUT_DIR)
    try:
        r = get_with_retries(url)
        df = pd.read_csv(BytesIO(r.content))
    except Exception as e:
        raise RuntimeError(
            f"Zillow download failed. URL may have changed. "
            f"Check https://www.zillow.com/research/data/ and set "
            f"ZILLOW_{dataset.upper()}_URL if needed. Error: {e}"
        ) from e
    out_name = timestamped_filename(f"zillow_{dataset}", "csv")
    out_path = OUTPUT_DIR / out_name
    df.to_csv(out_path, index=False)
    _log_ingest(df, out_path, dataset, "download", {"url": url})
    _update_sources(dataset, "download", {"url": url})
    print(f"Downloaded {len(df)} rows -> {out_path}")
    return out_path


def _log_ingest(
    df: pd.DataFrame,
    out_path: Path,
    dataset: str,
    mode: str,
    extra: dict,
) -> None:
    stats = dataframe_ingest_stats(df)
    write_ingest_log(
        {
            "source": "zillow",
            "dataset": dataset,
            "mode": mode,
            "file_path": str(out_path),
            "retrieval_date": datetime.now().isoformat(),
            **stats,
            **extra,
        }
    )


def _update_sources(dataset: str, mode: str, extra: dict) -> None:
    link = extra.get("url") or extra.get("inbox_file", "inbox")
    write_sources_md(
        {
            "source": f"Zillow Research ({dataset.upper()})",
            "retrieval_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "parameters": f"dataset={dataset}, mode={mode}",
            "link": link,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Acquire Zillow ZHVI/ZORI data")
    parser.add_argument("--dataset", choices=["zhvi", "zori"], default="zhvi", help="Dataset to acquire")
    parser.add_argument("--mode", choices=["inbox", "download"], required=True, help="inbox or download")
    args = parser.parse_args()
    if args.mode == "inbox":
        run_inbox(args.dataset)
    else:
        run_download(args.dataset)


if __name__ == "__main__":
    main()
