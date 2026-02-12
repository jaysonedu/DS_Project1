"""Loaders for smoke test: find newest raw file per source."""

from __future__ import annotations

from pathlib import Path

from ._utils import PROJECT_ROOT, RAW_DIR


def _newest_file(directory: Path, pattern: str = "*") -> Path | None:
    """Return path to most recently modified file matching pattern."""
    if not directory.exists():
        return None
    files = list(directory.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def load_newest_zillow() -> tuple[Path | None, object]:
    """Load newest Zillow CSV. Returns (path, df or None)."""
    import pandas as pd

    p = _newest_file(RAW_DIR / "zillow", "zillow_*.csv")
    if p is None:
        return None, None
    return p, pd.read_csv(p)


def load_newest_nyc_crime() -> tuple[Path | None, object]:
    """Load newest NYC crime parquet. Returns (path, df or None)."""
    import pandas as pd

    p = _newest_file(RAW_DIR / "nyc_crime", "*.parquet")
    if p is None:
        return None, None
    return p, pd.read_parquet(p)


def load_newest_acs() -> tuple[Path | None, object]:
    """Load newest ACS parquet. Returns (path, df or None)."""
    import pandas as pd

    p = _newest_file(RAW_DIR / "acs", "*.parquet")
    if p is None:
        return None, None
    return p, pd.read_parquet(p)


def load_newest_fred() -> tuple[Path | None, object]:
    """Load newest FRED CSV. Returns (path, df or None)."""
    import pandas as pd

    p = _newest_file(RAW_DIR / "fred", "*.csv")
    if p is None:
        return None, None
    return p, pd.read_csv(p)


def load_all_newest() -> dict[str, tuple[Path | None, object]]:
    """Load newest file from each source. Returns {source: (path, df)}."""
    return {
        "zillow": load_newest_zillow(),
        "nyc_crime": load_newest_nyc_crime(),
        "acs": load_newest_acs(),
        "fred": load_newest_fred(),
    }
