# NYC Housing + Neighborhood Factors

Data acquisition layer plus downstream notebooks for cleaning, EDA, and feature engineering.

## Setup

Python 3.11+, Git. From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Create a `.env` file with `FRED_API_KEY` (required for FRED) and optionally `CENSUS_API_KEY`. Copy from `.env.example` if present.

## Getting the data

Raw files go to `data/raw/<source>/`. Run from project root:

| Source | Command |
|--------|--------|
| Zillow | Put ZHVI CSV in `data/raw/zillow/inbox/`, then `python -m src.acquire.zillow --dataset zhvi --mode inbox` |
| NYC Crime | `python -m src.acquire.nyc_crime` (or `--start` / `--end` YYYY-MM-DD) |
| Census ACS | `python -m src.acquire.acs --year 2023` |
| FRED | `python -m src.acquire.fred` |
| Geo (optional) | `python -m src.acquire.geo` |

Zillow: if `--mode download` fails, use inbox and download from [Zillow Research Data](https://www.zillow.com/research/data/). NYPD: add `--dataset historic` for 2006–2019.

## Verify and use the data

- **Sanity check:** Open `notebooks/00_Data_Collection_Sanity_Check.ipynb` and run to load newest raw files and print shapes.
- **Load in code:** `from src.acquire._loaders import load_all_newest` then `load_all_newest()`.

Metadata: `data/metadata/sources.md`, `data/metadata/ingest_log.json`.

## Next steps

Cleaning and merging: see [docs/CLEANING_AND_MERGING.md](docs/CLEANING_AND_MERGING.md). Notebooks: `01_EDA_Analysis`, `02_Data_Preprocessing`, `03_FeatureEngineer`.
