# NYC Housing + Neighborhood Factors — Data Acquisition

Data acquisition layer for a housing + neighborhood data science project. **Acquisition only** — no cleaning or EDA.

## Setup

```bash
pip install -e .
```

### API Keys (optional)

- **Census ACS**: Set `CENSUS_API_KEY` (recommended for higher rate limits)
- **FRED**: Set `FRED_API_KEY` (required for FRED API)

## CLI Usage

```bash
# Zillow: inbox mode (drop CSV in data/raw/zillow/inbox/)
python -m src.acquire.zillow --dataset zhvi --mode inbox

# Zillow: download mode (uses stable URL if configured)
python -m src.acquire.zillow --dataset zhvi --mode download

# NYC Crime: date range
python -m src.acquire.nyc_crime --start 2022-01-01 --end 2024-12-31

# Census ACS: ZCTA-level socioeconomic data
python -m src.acquire.acs --year 2023

# FRED: mortgage & Fed funds rates
python -m src.acquire.fred --start 2022-01-01 --end 2024-12-31

# Geo helpers: ZIP/ZCTA boundaries
python -m src.acquire.geo
```

## Defaults

- **Location**: NYC
- **Date window**: Last 36 months ending today

## Outputs

- Raw files: `data/raw/<source>/` with timestamped filenames
- Metadata: `data/metadata/sources.md`, `data/metadata/ingest_log.json`
- Smoke test: `notebooks/00_smoke_test.ipynb`

## Notes

- **Zillow**: Download URLs may change. If `--mode download` fails, use `--mode inbox` and manually download from [Zillow Research Data](https://www.zillow.com/research/data/), or set `ZILLOW_ZHVI_URL` / `ZILLOW_ZORI_URL`.
- **NYPD**: Use `--dataset historic` for 2006–2019; `current` for year-to-date.
