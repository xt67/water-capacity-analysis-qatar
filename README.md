# 💧 Qatar Water Intelligence
### Reservoir Capacity Analysis & Interactive Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)
![Scikit--learn](https://img.shields.io/badge/Scikit--learn-Unsupervised%20ML-F7931E?logo=scikitlearn&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-SQL%20Analytics-4169E1?logo=postgresql&logoColor=white)

**Qatar Water Intelligence** is a data analytics project that examines reservoir storage capacity across Qatar using KAHRAMAA's 2023 station-level dataset. It combines a reproducible Python data pipeline, exploratory analysis, unsupervised machine learning, PostgreSQL queries, and an interactive Streamlit dashboard.

The project builds on work completed during a **Data Analyst Internship at KAHRAMAA in July 2025**. The underlying observations are a historical **2023 snapshot**, not live operational data.

**Live dashboard:** https://water-capacity-analysis.streamlit.app/

---

## Project Overview

The analysis explores how installed water-storage capacity is distributed across stations, how concentrated that capacity is, and how stations can be grouped by their capacity profiles.

It also documents the difference between the station-level dataset subtotal and the national storage figure published by KAHRAMAA.

### Key Findings

- The cleaned dataset contains **39 station records**, including 38 operational stations and Old Salwa, whose reservoirs were demolished for upgrading.
- The 38 operational station records sum to **2,415.53 MIG** (approximately **10,979,662 m³**).
- KAHRAMAA's Annual Statistics Report 2023 reports national water storage of **2,417.2 MIG** (approximately **10,987,273 m³**).
- The difference is approximately **1.67 MIG / 7,611 m³**, or 0.07%.
- The five largest stations account for approximately **58.8%** of the operational station-file subtotal.
- The Gini coefficient is approximately **0.673**.
- Clustering identifies descriptive capacity tiers, not predictions of demand, failures, or operational performance.

![Capacity by station](charts/01_capacity_by_station.png)

## Features

| Component | Implementation |
|---|---|
| Data preparation | Python-based cleaning, transformation, and validation |
| Exploratory analysis | Station capacity, station types, and storage distribution |
| Machine learning | K-Means clustering, silhouette analysis, robust size-rarity checks |
| Statistical analysis | Gini coefficient, cumulative storage shares, top-N concentration |
| Interactive dashboard | Streamlit and Plotly |
| Database | PostgreSQL schema, validation, and analysis queries |
| Business intelligence | Power BI correction guide and DAX documentation |
| External data | Optional Qatar Open Data and World Bank data-fetching pipeline |

## Technology Stack

- Python
- Pandas and NumPy
- Scikit-learn
- Plotly and Matplotlib
- Streamlit
- PostgreSQL
- Power BI
- Git and GitHub

## Machine Learning Approach

The station dataset contains one independent numeric feature suitable for station-level grouping: installed capacity. The cubic-metre values are unit conversions of MIG, not independent measurements.

Therefore, this project uses descriptive unsupervised techniques rather than claiming to train a supervised prediction model.

1. **Capacity tiering:** K-Means clustering on log-transformed capacity, with candidate cluster counts evaluated using silhouette scores.
2. **Size rarity:** Robust median-absolute-deviation scores to identify unusually small or large capacities.
3. **Storage concentration:** Cumulative capacity shares, top-N concentration, and Gini coefficient.

A credible demand forecast or time-series model would require multiple years of comparable storage, production, consumption, and demand data.

## Data Sources

- [KAHRAMAA Annual Statistics Report 2023](https://www.km.com.qa/MediaCenter/Publications/SR2023-English.pdf)
- [Qatar Open Data: Water Storage in KM Reservoirs (2023)](https://www.data.gov.qa/explore/dataset/water-storage-in-km-reservoirs-2023/)
- [Qatar Open Data: Total Water Storage by Year](https://www.data.gov.qa/explore/dataset/total-water-storage-by-year/table/)
- [Qatar Open Data: Ground Tanks](https://www.data.gov.qa/explore/dataset/water-storage-in-ground-tanks-2023/)
- [Qatar Open Data: Elevated Tanks](https://www.data.gov.qa/explore/dataset/water-storage-in-elevated-tanks-2023/)
- [Qatar Open Data: IWPP Reservoirs](https://www.data.gov.qa/explore/dataset/water-storage-in-iwpp-reservoirs-2023/)
- [World Bank: Freshwater Withdrawals Indicator Metadata](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/ER.H2O.FWTL.ZS)

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/xt67/water-capacity-analysis-qatar.git
cd water-capacity-analysis-qatar
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

The dashboard will be available at:

`http://localhost:8501`

## Rebuild the Analysis Pipeline

Install the full pipeline dependencies:

```bash
pip install -r requirements-pipeline.txt
```

Run the scripts in order:

```bash
python src/build_dataset.py
python src/ml_models.py
python src/make_charts.py
```

### Optional External Data Downloads

```bash
cp .env.example .env
python src/fetch_external.py
```

Kaggle downloads require valid credentials and a verified dataset slug in `.env`.

```bash
python src/fetch_external.py --include-kaggle
```

Review dataset licences, provenance, schemas, and reporting periods before using external data. Credentials and downloaded external datasets should not be committed to Git.

## PostgreSQL Workflow

1. Run `sql/01_create_table.sql`.
2. Import `data/water_stations_qatar_clean.csv`.
3. Run `sql/02_validate.sql`.
4. Execute `sql/03_analysis_queries.sql`.

## Repository Structure

```text
.
├── app.py
├── .streamlit/
├── data/
├── src/
│   ├── build_dataset.py
│   ├── ml_models.py
│   ├── make_charts.py
│   └── fetch_external.py
├── sql/
├── charts/
├── dashboard/
├── requirements.txt
└── requirements-pipeline.txt
```

## Deployment

The dashboard is built with Streamlit and can be deployed using **Streamlit Community Cloud**.

For a fresh deployment:

1. Connect the GitHub repository to Streamlit Community Cloud.
2. Select the `main` branch.
3. Set `app.py` as the application entry point.
4. Deploy.

The basic dashboard uses committed data files and does not require an external database or API credentials.

## Limitations and Responsible Interpretation

- The analysis represents the 2023 reporting period, not live water infrastructure conditions.
- The station-level subtotal and national aggregate represent different scopes.
- Clustering describes capacity groups, not operational risk or station performance.
- No demand forecasting or failure prediction is claimed.
- External datasets should be checked for compatible definitions and reporting periods before integration.

## Author

**Rayan Rahman**
GitHub: [@xt67](https://github.com/xt67)

## Licence

See the [LICENSE](LICENSE) file included in this repository.
