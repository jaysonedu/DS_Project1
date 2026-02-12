# Data Cleaning and Merging Guide

This document guides the exploration and preprocessing team through cleaning the raw data and merging it into an analysis-ready dataset for NYC housing + neighborhood factors.

---

## 1. Raw Data Overview

| Source | Location | Geography | Time | Key Fields |
|--------|----------|-----------|------|------------|
| **Zillow ZHVI** | `data/raw/zillow/` | ZIP (`RegionName`) | Monthly (date columns) | Home value index by month |
| **NYC Crime** | `data/raw/nyc_crime/` | Incident (precinct, lat/lon, borough) | `cmplnt_fr_dt` | Complaint-level incidents |
| **ACS** | `data/raw/acs/` | ZCTA (`zip code tabulation area`) | 5-year snapshot | Population, income, poverty, education, unemployment |
| **FRED** | `data/raw/fred/` | National | Daily/weekly | Mortgage rate, Fed funds rate |

Use `src.acquire._loaders.load_all_newest()` to load the most recent raw file from each source.

---

## 2. Cleaning Steps by Source

### 2.1 Zillow ZHVI

**Structure:** Wide format — geography columns (`RegionID`, `RegionName`, `State`, etc.) + monthly date columns (e.g. `2000-01-31`, `2024-12-31`).

**Steps:**
1. Filter to NYC area: `State == "NY"` (or filter by `RegionName` for NYC ZIP codes: 100xx, 101xx, 102xx, 104xx, 110xx, 111xx, 112xx, 113xx, 114xx, 116xx).
2. Select date range: keep only columns for your analysis window (e.g. last 36 months).
3. Unpivot: melt date columns to long format so each row is (ZIP, date, value).
4. Handle missing values: Zillow uses `NaN` for some ZIPs in some months — decide whether to drop, forward-fill, or interpolate.
5. Rename for clarity: `RegionName` → `zip`, date column → `month`, value → `zhvi`.

### 2.2 NYC Crime

**Structure:** One row per incident. Key columns: `cmplnt_num`, `cmplnt_fr_dt`, `boro_nm`, `addr_pct_cd`, `latitude`, `longitude`, `law_cat_cd`, `ofns_desc`, etc.

**Steps:**
1. Parse dates: `cmplnt_fr_dt` is datetime — convert to date and filter to your analysis window.
2. Handle nulls: check `latitude`, `longitude`, `addr_pct_cd` for missing values (some incidents may lack location).
3. Aggregate to geography × time: crime has no ZIP — you must:
   - **Option A:** Use `addr_pct_cd` (precinct) and a precinct-to-ZIP crosswalk (NYC Open Data or manual mapping).
   - **Option B:** Spatial join `latitude`/`longitude` to ZCTA boundaries (from `data/raw/geo/`) to assign each incident to a ZCTA, then aggregate counts by (ZCTA, month).
4. Create derived metrics: e.g. total complaints per ZIP/month, felony count, violent vs. property crime (using `law_cat_cd`, `ofns_desc`).

### 2.3 ACS (Census)

**Structure:** One row per ZCTA. Variables: `B01003_001E` (population), `B19013_001E` (median income), `B17001_001E/002E` (poverty), `B23025_003E/005E` (labor force, unemployed), `B15003_022E`–`025E` (education).

**Steps:**
1. Filter to NYC ZCTAs: keep rows where `zip code tabulation area` is in NYC ZIP ranges (see above).
2. Handle Census nulls: Census uses large negative values (e.g. `-666666666`) for missing — already converted to `NaN` in acquisition; verify and drop or impute as needed.
3. Rename columns to readable names, e.g.:
   - `B01003_001E` → `population`
   - `B19013_001E` → `median_household_income`
   - `B17001_002E` / `B17001_001E` → `poverty_rate` (compute as ratio)
   - `B23025_005E` / `B23025_003E` → `unemployment_rate`
   - Sum `B15003_022E`–`025E` for `bachelors_plus`
4. ACS is a 5-year snapshot (e.g. 2019–2023 for 2023 release) — treat as constant across months within that period, or note the reference year.

### 2.4 FRED

**Structure:** Long format — `date`, `series_id`, `value`. Two series: `MORTGAGE30US`, `FEDFUNDS`.

**Steps:**
1. Pivot: one column per series (`mortgage_rate`, `fed_funds_rate`).
2. Resample to monthly: FRED may be weekly/daily — aggregate to month-end or month-average to match Zillow.
3. Forward-fill if needed: rates are national and can be joined to all ZIPs in a given month.

---

## 3. Geography Alignment: ZIP vs. ZCTA

- **Zillow** uses USPS **ZIP codes** (`RegionName`).
- **ACS** uses **ZCTAs** (`zip code tabulation area`).
- **Crime** uses precincts and lat/lon — no direct ZIP.

**ZIP ≈ ZCTA** for most NYC areas (same 5-digit codes). Use ZIP/ZCTA as the common key where they align. For strict matching, use a [ZIP–ZCTA crosswalk](https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html) if needed.

**NYC ZIP prefixes (boroughs):**
- Manhattan: 100xx, 101xx, 102xx
- Bronx: 104xx
- Brooklyn: 112xx
- Queens: 111xx, 113xx, 114xx, 116xx
- Staten Island: 103xx

---

## 4. Merging Strategy

Target: one row per **(ZIP/ZCTA, month)** with housing, neighborhood, and macro features.

### Join structure

```
base = (ZIP, month) from Zillow (after filter to NYC + unpivot)
       ↓
ACS: left join on ZIP = ZCTA (ACS is cross-sectional; repeat for each month or add year)
       ↓
Crime: left join on ZIP (or ZCTA) and month (aggregated counts)
       ↓
FRED: left join on month (national rates, same for all ZIPs)
```

### Example workflow (pseudocode)

```python
# 1. Zillow: filter NYC, unpivot, rename
zhvi_long = zhvi.filter(State == "NY").melt(id_vars=[...], var_name="month", value_name="zhvi")

# 2. ACS: filter NYC, rename, compute derived vars
acs_nyc = acs[acs["zip code tabulation area"].isin(nyc_zips)].rename(columns={...})

# 3. Crime: spatial join or precinct crosswalk → aggregate (ZCTA, month) counts
crime_by_zcta_month = ...

# 4. FRED: pivot and resample to monthly
fred_monthly = fred.pivot(index="date", columns="series_id", values="value").resample("ME").mean()

# 5. Merge
merged = zhvi_long.merge(acs_nyc, left_on="zip", right_on="zcta", how="left")
merged = merged.merge(crime_by_zcta_month, on=["zip", "month"], how="left")
merged = merged.merge(fred_monthly, left_on="month", right_index=True, how="left")
```

---

## 5. Output for Modeling

Save the cleaned, merged dataset to:

```
data/processed/model_data.parquet
```

Suggested schema:
- `zip` or `zcta`: geography
- `month`: time
- `zhvi`: target or feature
- `population`, `median_income`, `poverty_rate`, `unemployment_rate`, `bachelors_plus`: ACS
- `crime_count`, `violent_crime_count`, etc.: crime
- `mortgage_rate`, `fed_funds_rate`: FRED

---

## 6. Next Steps After Cleaning

1. **EDA:** Distributions, correlations, time trends, maps (ZIP-level choropleths).
2. **Target definition:** e.g. ZHVI level, YoY change, or future change.
3. **Feature engineering:** lags, rolling stats, crime per capita, etc.
4. **Modeling:** regression, forecasting, or causal analysis depending on project goals.

---

## 7. Resources

- **Ingest log:** `data/metadata/ingest_log.json` — row counts, columns, null counts per run.
- **Source metadata:** `data/metadata/sources.md` — retrieval dates and parameters.
- **Loaders:** `from src.acquire._loaders import load_all_newest`
