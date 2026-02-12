"""US Census ACS 5-year data: ZCTA-level socioeconomic variables."""

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

# ACS 5-year detailed table variables (ZCTA-level)
# B01003_001E: Total population
# B19013_001E: Median household income
# B17001_001E: Poverty universe total
# B17001_002E: Income below poverty
# B23025_003E: In labor force
# B23025_005E: Unemployed
# B15003_022E..025E: Bachelor's, Master's, Professional, Doctorate
ACS_VARIABLES = [
    "NAME",
    "B01003_001E",  # Total population
    "B19013_001E",  # Median household income
    "B17001_001E",  # Poverty universe
    "B17001_002E",  # Below poverty
    "B23025_003E",  # In labor force
    "B23025_005E",  # Unemployed
    "B15003_022E",  # Bachelor's degree
    "B15003_023E",  # Master's degree
    "B15003_024E",  # Professional degree
    "B15003_025E",  # Doctorate degree
]
CENSUS_BASE = "https://api.census.gov/data"

# NYC focus: New York State (FIPS 36) — ZCTAs cover the state including NYC
STATE_NY = "36"


def fetch_acs_zcta(year: int, *, state: str | None = None) -> pd.DataFrame:
    """Fetch ACS 5-year ZCTA data for given year.
    ZCTAs do not nest within states per Census API, so we fetch all US ZCTAs.
    Filter to NY/NYC ZCTAs during cleaning if needed.
    """
    key = get_env("CENSUS_API_KEY", required=False)
    url = f"{CENSUS_BASE}/{year}/acs/acs5"
    params: dict = {
        "get": ",".join(ACS_VARIABLES),
        "for": "zip code tabulation area:*",
    }
    if key:
        params["key"] = key
    r = get_with_retries(url, params=params)
    data = r.json()
    if not data:
        raise RuntimeError("Census API returned empty response")
    headers = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=headers)
    # Census returns -666666666 etc for missing; convert to NaN
    for col in df.columns:
        if col in ("NAME", "state", "zip code tabulation area"):
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[df[col] < -1e9, col] = pd.NA
    return df


def run(year: int, *, state: str | None = None) -> Path:
    """Acquire ACS 5-year ZCTA data and save as parquet."""
    ensure_dirs(RAW_DIR / "acs")
    df = fetch_acs_zcta(year, state=state)
    out_name = timestamped_filename(f"acs_{year}", "parquet")
    out_path = RAW_DIR / "acs" / out_name
    df.to_parquet(out_path, index=False)
    stats = dataframe_ingest_stats(df)
    write_ingest_log(
        {
            "source": "acs",
            "file_path": str(out_path),
            "retrieval_date": datetime.now().isoformat(),
            "parameters": f"year={year}, state={'all' if not state else state}",
            **stats,
        }
    )
    write_sources_md(
        {
            "source": "US Census ACS 5-Year",
            "retrieval_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "parameters": f"year={year}, ZCTA-level (nationwide)",
            "link": f"{CENSUS_BASE}/{year}/acs/acs5",
        }
    )
    print(f"Acquired {len(df)} ZCTAs -> {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Acquire Census ACS 5-year ZCTA data")
    parser.add_argument("--year", type=int, required=True, help="ACS release year (e.g. 2023)")
    parser.add_argument(
        "--state",
        default=None,
        help="Unused; ZCTAs fetched nationwide (filter during cleaning)",
    )
    args = parser.parse_args()
    run(args.year, state=args.state)


if __name__ == "__main__":
    main()
