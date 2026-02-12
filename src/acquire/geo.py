"""Geo helpers: ZCTA boundaries and ZIP/ZCTA crosswalks."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from ._utils import RAW_DIR, ensure_dirs, write_sources_md
from ._http import get_with_retries

# Census TIGER ZCTA 5-digit boundaries (national, ~504MB)
ZCTA_SHAPEFILE_URL = "https://www2.census.gov/geo/tiger/TIGER2023/ZCTA520/tl_2023_us_zcta520.zip"
GEO_DIR = RAW_DIR / "geo"


def run(*, year: int = 2023) -> Path:
    """Download ZCTA boundary shapefile and store in data/raw/geo/."""
    ensure_dirs(GEO_DIR)
    # Use 2023 ZCTA520
    url = ZCTA_SHAPEFILE_URL
    out_name = f"tl_{year}_us_zcta520_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    out_path = GEO_DIR / out_name
    try:
        r = get_with_retries(url, timeout=120)
        out_path.write_bytes(r.content)
    except Exception as e:
        raise RuntimeError(
            f"Failed to download ZCTA boundaries. URL may have changed. "
            f"Check https://www.census.gov/cgi-bin/geo/shapefiles/index.php. Error: {e}"
        ) from e
    write_sources_md(
        {
            "source": "Census TIGER/Line ZCTA Boundaries",
            "retrieval_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "parameters": f"year={year}, ZCTA520",
            "link": "https://www2.census.gov/geo/tiger/TIGER2023/ZCTA520/",
        }
    )
    print(f"Downloaded ZCTA boundaries -> {out_path} ({len(out_path.read_bytes()) / 1e6:.1f} MB)")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Acquire ZCTA boundary files")
    parser.add_argument("--year", type=int, default=2023, help="TIGER release year")
    args = parser.parse_args()
    run(year=args.year)


if __name__ == "__main__":
    main()
