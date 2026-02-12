"""NYC Open Data: NYPD Complaint Data via Socrata API."""

from __future__ import annotations

import argparse
from datetime import datetime
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

# NYC Open Data Socrata endpoints
# Current YTD: 5uac-w243 | Historic (2006-2019): qgea-i56i
NYPD_CURRENT_ID = "5uac-w243"
NYPD_HISTORIC_ID = "qgea-i56i"
SOCRATA_LIMIT = 50000  # Max rows per request


def _parse_date(s: str) -> str:
    """Ensure date string for Socrata $where clause."""
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%dT00:00:00")
    except ValueError:
        raise ValueError(f"Invalid date format: {s}. Use YYYY-MM-DD.") from None


def fetch_nypd_date_range(
    start: str,
    end: str,
    *,
    dataset_id: str = NYPD_CURRENT_ID,
) -> pd.DataFrame:
    """Fetch NYPD complaint data for date range with pagination."""
    base = f"https://data.cityofnewyork.us/resource/{dataset_id}.json"
    start_ts = _parse_date(start)
    end_ts = _parse_date(end)
    where = f"cmplnt_fr_dt >= '{start_ts}' and cmplnt_fr_dt <= '{end_ts}'"
    params: dict = {
        "$limit": SOCRATA_LIMIT,
        "$offset": 0,
        "$where": where,
    }
    rows: list[dict] = []
    while True:
        r = get_with_retries(base, params=params)
        data = r.json()
        if not data:
            break
        rows.extend(data)
        if len(data) < SOCRATA_LIMIT:
            break
        params["$offset"] += SOCRATA_LIMIT
    return pd.DataFrame(rows)


def run(start: str, end: str, *, dataset: str = "current") -> Path:
    """Acquire NYPD complaint data and save as parquet."""
    dataset_id = NYPD_HISTORIC_ID if dataset == "historic" else NYPD_CURRENT_ID
    ensure_dirs(RAW_DIR / "nyc_crime")
    df = fetch_nypd_date_range(start, end, dataset_id=dataset_id)
    out_name = timestamped_filename("nyc_crime", "parquet")
    out_path = RAW_DIR / "nyc_crime" / out_name
    df.to_parquet(out_path, index=False)
    stats = dataframe_ingest_stats(df)
    write_ingest_log(
        {
            "source": "nyc_crime",
            "file_path": str(out_path),
            "retrieval_date": datetime.now().isoformat(),
            "parameters": f"start={start}, end={end}, dataset={dataset}",
            **stats,
        }
    )
    write_sources_md(
        {
            "source": "NYC Open Data / NYPD Complaint Data",
            "retrieval_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "parameters": f"start={start}, end={end}, dataset={dataset}",
            "link": f"https://data.cityofnewyork.us (dataset={dataset_id})",
        }
    )
    print(f"Acquired {len(df)} rows -> {out_path}")
    return out_path


def _default_date_range(months: int = 36) -> tuple[str, str]:
    """Default: last N months ending today."""
    from datetime import date, timedelta

    end = date.today()
    start = end - timedelta(days=months * 31)  # approximate
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def main() -> None:
    parser = argparse.ArgumentParser(description="Acquire NYPD Complaint Data")
    parser.add_argument("--start", help="Start date YYYY-MM-DD (default: 36 months ago)")
    parser.add_argument("--end", help="End date YYYY-MM-DD (default: today)")
    parser.add_argument(
        "--dataset",
        choices=["current", "historic"],
        default="current",
        help="current=YTD, historic=2006-2019",
    )
    args = parser.parse_args()
    start, end = args.start, args.end
    if not start or not end:
        def_start, def_end = _default_date_range(36)
        start = start or def_start
        end = end or def_end
    run(start, end, dataset=args.dataset)


if __name__ == "__main__":
    main()
