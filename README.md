# NYC Housing + Neighborhood Factors

DS Project 1: data acquisition, cleaning, EDA, feature engineering, and modeling for NYC housing and neighborhood factors.

## Project report

**Report.ipynb** (project root) is the structured report. It includes introduction and dataset description, data acquisition methodology, cleaning and preprocessing, EDA, feature engineering justification, key findings, challenges and recommendations, GitHub link, and team contributions. Export to PDF for submission: *File → Save and Export Notebook As… → PDF*, or `jupyter nbconvert --to pdf Report.ipynb`.

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

- **Sanity check:** `notebooks/00_Data_Collection_Sanity_Check.ipynb` — load newest raw files and print shapes.
- **Load in code:** `from src.acquire._loaders import load_all_newest` then `load_all_newest()`.

Metadata: `data/metadata/sources.md`, `data/metadata/ingest_log.json`.

## Notebooks and docs

- **Report.ipynb** — Full project report (export to PDF).
- **notebooks/** — `00_Data_Collection_Sanity_Check`, `01_EDA_Analysis`, `02_Data_Preprocessing`, `03_FeatureEngineer`.
- **docs/** — Data preprocessing report (PDF), feature engineering rationale, cleaning/merging guide, combined documentation.
