"""FRED API: Mortgage rate and Fed funds rate series."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from ._utils import (
    RAW_DIR,
    ensure_dirs,
    get_env,
    timestamped_filename,
    write_ingest_log,
    write_sources_md,
    dataframe_ingest_stats,
)
from ._http import get_with_retries

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
# 30-year fixed mortgage rate, Fed funds rate
FRED_SERIES = ["MORTGAGE30US", "FEDFUNDS"]


def fetch_fred_series(
    series_ids: list[str],
    start: str,
    end: str,
    *,
    api_key: str,
) -> pd.DataFrame:
    """Fetch FRED observations for given series and date range."""
    all_data: list[dict] = []
    for sid in series_ids:
        params = {
            "series_id": sid,
            "observation_start": start,
            "observation_end": end,
            "api_key": api_key,
            "file_type": "json",
        }
        r = get_with_retries(FRED_BASE, params=params)
        data = r.json()
        obs = data.get("observations", [])
        for o in obs:
            val = o.get("value", ".")
            all_data.append(
                {
                    "date": o["date"],
                    "series_id": sid,
                    "value": val if val != "." else None,
                }
            )
    df = pd.DataFrame(all_data)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def run(start: str, end: str, *, series: list[str] | None = None) -> Path:
    """Acquire FRED data and save as CSV."""
    key = get_env("FRED_API_KEY", required=True)
    ensure_dirs(RAW_DIR / "fred")
    ids = series or FRED_SERIES
    df = fetch_fred_series(ids, start, end, api_key=key)
    out_name = timestamped_filename("fred", "csv")
    out_path = RAW_DIR / "fred" / out_name
    df.to_csv(out_path, index=False)
    stats = dataframe_ingest_stats(df)
    write_ingest_log(
        {
            "source": "fred",
            "file_path": str(out_path),
            "retrieval_date": datetime.now().isoformat(),
            "parameters": f"start={start}, end={end}, series={ids}",
            **stats,
        }
    )
    write_sources_md(
        {
            "source": "FRED (St. Louis Fed)",
            "retrieval_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "parameters": f"start={start}, end={end}, series={ids}",
            "link": "https://fred.stlouisfed.org/docs/api/fred/",
        }
    )
    print(f"Acquired {len(df)} observations -> {out_path}")
    return out_path


def _default_date_range(months: int = 36) -> tuple[str, str]:
    """Default: last N months ending today."""
    from datetime import date, timedelta

    end = date.today()
    start = end - timedelta(days=months * 31)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def main() -> None:
    parser = argparse.ArgumentParser(description="Acquire FRED economic data")
    parser.add_argument("--start", help="Start date YYYY-MM-DD (default: 36 months ago)")
    parser.add_argument("--end", help="End date YYYY-MM-DD (default: today)")
    parser.add_argument(
        "--series",
        nargs="+",
        default=FRED_SERIES,
        help=f"FRED series IDs (default: {FRED_SERIES})",
    )
    args = parser.parse_args()
    start, end = args.start, args.end
    if not start or not end:
        def_start, def_end = _default_date_range(36)
        start = start or def_start
        end = end or def_end
    run(start, end, series=args.series)


if __name__ == "__main__":
    main()
