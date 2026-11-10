# 💧 Qatar Water Reservoir Capacity Analysis

**Internship:** KAHRAMAA, Data Analyst Intern, **July 2025**
**Data/reporting period:** **2023** (historical snapshot; intentionally not refreshed to today's date)

This project analyses Qatar's water reservoir and pumping-station storage capacity
using Python, pandas, scikit-learn, PostgreSQL, Power BI and an interactive Plotly
dashboard. The internship was completed in July 2025; the capacity observations
remain the 2023 data supplied by KAHRAMAA.

![Capacity by station](charts/01_capacity_by_station.png)

## Executive findings

- The cleaned station file contains **39 records**: **38 operational stations**
  plus Old Salwa, whose reservoirs were demolished for upgrading.
- The 38 operational KM station records sum to **2,415.53 MIG** and
  **10,979,662 m³**. This is the station-dataset subtotal, not the official
  national all-storage total.
- KAHRAMAA's Annual Statistics Report 2023 records national water storage of
  **2,417.2 MIG / 10,987,273 m³**. The difference from this station-level file
  is **1.67 MIG / 7,611 m³** (about 0.07%). It is retained as a reconciliation
  variance rather than allocated to stations without source evidence.
- Storage is concentrated: the top five stations hold about **58.8%** of the
  station-file subtotal; the Gini coefficient is about **0.673**.
- The model identifies four capacity tiers. These are descriptive groupings,
  not predictions of demand, station failure or operational performance.

Official sources:
- [KAHRAMAA Annual Statistics Report 2023](https://www.km.com.qa/MediaCenter/Publications/SR2023-English.pdf)
- [Qatar Open Data: Water Storage in KM Reservoirs (2023)](https://www.data.gov.qa/explore/dataset/water-storage-in-km-reservoirs-2023/)
- [Qatar Open Data: Total Water Storage by Year](https://www.data.gov.qa/explore/dataset/total-water-storage-by-year/table/)
- [Qatar Open Data: Ground Tanks](https://www.data.gov.qa/explore/dataset/water-storage-in-ground-tanks-2023/)
- [Qatar Open Data: Elevated Tanks](https://www.data.gov.qa/explore/dataset/water-storage-in-elevated-tanks-2023/)
- [Qatar Open Data: IWPP Reservoirs](https://www.data.gov.qa/explore/dataset/water-storage-in-iwpp-reservoirs-2023/)
- [World Bank indicator metadata: freshwater withdrawals](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/ER.H2O.FWTL.ZS)

## Work completed in this repository

| Area | Implementation |
|---|---|
| Date integrity | Internship date is July 2025; source reporting year remains 2023 in filenames, `data_year`, charts and SQL. |
| Data cleaning | `src/build_dataset.py` rebuilds the station CSV from the source XLSX and validates capacity arithmetic and MIG-to-m³ conversion. |
| ML | `src/ml_models.py` performs unsupervised capacity tiering, robust size-rarity checks and concentration analysis. No predictive model is claimed because the source has only one capacity snapshot. |
| Visuals | Five static PNG charts plus the interactive `dashboard/dashboard.html`. |
| Power BI | `dashboard/POWERBI_FIXES.md` contains corrected DAX measures and explicit guidance to distinguish the station subtotal from the national aggregate. |
| SQL | Table creation, validation, national summary, Pareto ranking, type mix and commissioning queries in `sql/`. |
| External data | `src/fetch_external.py` downloads official Qatar Open Data exports and World Bank context series. Kaggle is optional and requires a verified dataset slug and personal credentials in local `.env`. |

## Machine-learning interpretation

The station table has 38 operational observations and only one independent
numeric characteristic suitable for this analysis: capacity. The m³ field is a
unit conversion of MIG, not a second independent feature. Therefore the models
are intentionally descriptive:

1. **K-Means capacity tiers** on log-transformed capacity, with the number of
   clusters selected by silhouette score.
2. **Robust size rarity** on log capacity. Small stations are not labelled as
   faults, risk or poor performance.
3. **Storage concentration** using Pareto share and the Gini coefficient.

A time-series forecast or demand model requires multiple years of comparable
storage, production, consumption and population/demand observations. It should
not be fabricated from this cross-sectional snapshot.

## Streamlit dashboard

A minimal interactive dashboard (`app.py`) reads the committed files in `data/`, so it needs no
database, API key or pipeline run.

```bash
pip install -r requirements.txt
streamlit run app.py
```

**Deploy on Streamlit Community Cloud (free):**
1. Push this repo to GitHub (the repo must be public, or your Streamlit account must be linked to it).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **Create app** → **Deploy a public app from GitHub**.
3. Repository: `xt67/water-capacity-analysis-qatar` · Branch: `main` · Main file path: `app.py`.
4. Deploy. Streamlit installs `requirements.txt` (only streamlit, pandas, plotly) automatically.

After deploying, paste the app URL at the top of this README. To refresh the data, rerun the
pipeline below and commit the updated files in `data/`; the app picks them up on the next deploy.

## Reproduce locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-pipeline.txt
python src/build_dataset.py
python src/ml_models.py
python src/make_charts.py
```

Optional external context downloads (internet required):

```bash
cp .env.example .env     # Windows: copy .env.example .env
python src/fetch_external.py
```

To additionally download a Kaggle dataset, fill in `KAGGLE_USERNAME`,
`KAGGLE_KEY` and a verified `KAGGLE_DATASET=owner/dataset-slug` in `.env`, then run:

```bash
python src/fetch_external.py --include-kaggle
```

Review Kaggle licence, provenance, schema and date coverage before using its data.
Downloaded files are stored under `data/external/` and are ignored by Git so that
credentials and unreviewed third-party datasets do not enter the repository.

## PostgreSQL

Run `sql/01_create_table.sql`, import
`data/water_stations_qatar_clean.csv` using the documented `\\copy` command,
then execute `sql/02_validate.sql` and `sql/03_analysis_queries.sql`.

## Repository layout

```text
app.py       Streamlit dashboard (deploy this file)
.streamlit/  Streamlit theme config
data/        Original 2023 XLSX, cleaned station CSV and ML outputs
src/         Cleaning, ML, chart/dashboard generation, optional data downloads
sql/         PostgreSQL schema, validation and analysis
charts/      Static PNG charts
dashboard/   Interactive dashboard, Power BI file and correction guide
```

## Notes

The `.pbix` is retained as the original Power BI artifact. Binary Power BI
editing is not performed by the Python pipeline; follow `dashboard/POWERBI_FIXES.md`
in Power BI Desktop. Do not replace the historical data year with the internship
or current calendar year.
