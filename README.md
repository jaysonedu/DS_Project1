# NYC Housing + Neighborhood Factors — Data Acquisition

Data acquisition layer for a housing + neighborhood data science project. **Acquisition only** — no cleaning or EDA. Raw data is saved for downstream exploration and preprocessing.

---

## Quick Start (Mac)

### 1. Prerequisites

- **Python 3.11+**  
  Check: `python3 --version`
- **Git**

### 2. Clone and enter the project

```bash
git clone <repo-url>
cd project1
```

### 3. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -e .
```

### 5. API keys (required for FRED, optional for Census)

Create a `.env` file in the project root:

```bash
touch .env
```

Add your keys (copy from `.env.example` if available):

```
FRED_API_KEY=your_fred_api_key_here
CENSUS_API_KEY=your_census_api_key_here
```

- **FRED**: Required. Get a free key at [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html)
- **Census**: Optional but recommended (higher rate limits). Get one at [census.gov/data/developers/api-key.html](https://api.census.gov/data/key_signup.html)

---

## Getting the Datasets

Run these commands in order. Raw files are written to `data/raw/<source>/`.

### 1. Zillow (housing values)

**Option A — Inbox (recommended):**

1. Download the ZHVI CSV from [Zillow Research Data](https://www.zillow.com/research/data/)
   - Choose “ZIP code” level, “Smoothed, Seasonally Adjusted”
2. Place the CSV in `data/raw/zillow/inbox/`
3. Run:

```bash
python -m src.acquire.zillow --dataset zhvi --mode inbox
```

**Option B — Direct download** (URLs may change):

```bash
python -m src.acquire.zillow --dataset zhvi --mode download
```

### 2. NYC Crime (NYPD complaints)

Uses the last 36 months by default:

```bash
python -m src.acquire.nyc_crime
```

Or specify dates:

```bash
python -m src.acquire.nyc_crime --start 2022-01-01 --end 2024-12-31
```

### 3. Census ACS (socioeconomic by ZCTA)

```bash
python -m src.acquire.acs --year 2023
```

### 4. FRED (mortgage & Fed funds rates)

Uses the last 36 months by default:

```bash
python -m src.acquire.fred
```

Or specify dates:

```bash
python -m src.acquire.fred --start 2022-01-01 --end 2024-12-31
```

### 5. Geo (ZCTA boundaries, optional)

```bash
python -m src.acquire.geo
```

---

## Verify the Data

Run the smoke test notebook to load the newest raw file from each source and print shapes:

```bash
jupyter notebook notebooks/00_smoke_test.ipynb
```

Or from a notebook environment: open `notebooks/00_smoke_test.ipynb` and run all cells.

---

## Next Steps: Cleaning & Merging

See **[docs/CLEANING_AND_MERGING.md](docs/CLEANING_AND_MERGING.md)** for guidance on cleaning each dataset, aligning geographies (ZIP/ZCTA), merging, and producing a modeling-ready dataset.

---

## Outputs (for exploration & preprocessing)

| Output             | Location                              |
|--------------------|----------------------------------------|
| Raw data           | `data/raw/zillow/`, `data/raw/nyc_crime/`, `data/raw/acs/`, `data/raw/fred/`, `data/raw/geo/` |
| Source metadata    | `data/metadata/sources.md`             |
| Ingest log         | `data/metadata/ingest_log.json`        |

Your group can use `src.acquire._loaders` to load the newest raw files:

```python
from src.acquire._loaders import load_all_newest

results = load_all_newest()
for source, (path, df) in results.items():
    # path, df for each source
    pass
```

---

## Notes

- **Zillow**: If `--mode download` fails, use `--mode inbox` and manually download from [Zillow Research Data](https://www.zillow.com/research/data/).
- **NYPD**: Use `--dataset historic` for 2006–2019; `current` is the default (year-to-date).
- **Defaults**: Location focus is NYC; date window is last 36 months where applicable.
