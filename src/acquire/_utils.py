"""Shared utilities for data acquisition."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# Default project root: parent of src/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
RAW_DIR = PROJECT_ROOT / "data" / "raw"
META_DIR = PROJECT_ROOT / "data" / "metadata"
INGEST_LOG_PATH = META_DIR / "ingest_log.json"
SOURCES_MD_PATH = META_DIR / "sources.md"

# Retry and timeout defaults
DEFAULT_TIMEOUT = 60
DEFAULT_RETRIES = 3
DEFAULT_RETRY_BACKOFF = 2.0


def ensure_dirs(*paths: Path) -> None:
    """Create directories if they do not exist."""
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def timestamped_filename(prefix: str, ext: str) -> str:
    """Generate a timestamped filename: prefix_YYYYMMDD_HHMMSS.ext"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{ext}"


def write_sources_md(entry: dict[str, str]) -> None:
    """Append or update sources.md with acquisition metadata."""
    ensure_dirs(META_DIR)
    entry_lines = [
        f"\n### {entry.get('source', 'Unknown')}",
        f"- **Retrieval date**: {entry.get('retrieval_date', '')}",
        f"- **Parameters**: {entry.get('parameters', '')}",
        f"- **Link/Endpoint**: {entry.get('link', '')}",
    ]
    content = "\n".join(entry_lines) + "\n"
    if SOURCES_MD_PATH.exists():
        with open(SOURCES_MD_PATH, "a", encoding="utf-8") as f:
            f.write(content)
    else:
        header = "# Data Sources\n"
        with open(SOURCES_MD_PATH, "w", encoding="utf-8") as f:
            f.write(header + content)


def write_ingest_log(entry: dict) -> None:
    """Append to ingest_log.json with row count, columns, null counts, file path."""
    ensure_dirs(META_DIR)
    logs: list[dict] = []
    if INGEST_LOG_PATH.exists():
        try:
            with open(INGEST_LOG_PATH, encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    if not isinstance(logs, list):
        logs = [logs] if isinstance(logs, dict) else []
    logs.append(entry)
    with open(INGEST_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)


def dataframe_ingest_stats(df: pd.DataFrame) -> dict:
    """Compute row count, columns, and null counts for a DataFrame."""
    return {
        "row_count": int(len(df)),
        "columns": list(df.columns),
        "null_counts": df.isna().sum().astype(int).to_dict(),
    }


def get_env(key: str, required: bool = False) -> str | None:
    """Get env var; raise if required and missing. Loads from .env in project root."""
    val = os.environ.get(key)
    if required and not val:
        raise EnvironmentError(
            f"Missing required environment variable: {key}. "
            f"Add it to .env in the project root or set it in your shell."
        )
    return val
