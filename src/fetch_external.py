"""OPTIONAL: pull supplementary public data to run on your own machine.

The core analysis does not need this script. It was NOT executed while the repo
was being fixed (the build sandbox could not reach these hosts), so treat it as
a starting point and check the output.

Setup:
  pip install -r requirements.txt
  cp .env.example .env     # then fill in the values you need
  python src/fetch_external.py

Sources
  * World Bank Open Data API - no key needed. Qatar population and freshwater
    withdrawal, useful as demand-side context for storage capacity.
  * Kaggle - needs KAGGLE_USERNAME / KAGGLE_KEY (kaggle.com > Settings > API).
    Set KAGGLE_DATASET to an "owner/dataset-slug" you have checked exists.
  * Qatar Open Data Portal (data.gov.qa) - the original source; download manually.
"""
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
EXT = ROOT / "data" / "external"
EXT.mkdir(parents=True, exist_ok=True)
load_dotenv(ROOT / ".env")

WB_INDICATORS = {
    "SP.POP.TOTL": "population",
    "ER.H2O.FWTL.ZS": "freshwater_withdrawal_pct_of_resources",
}


def fetch_world_bank(country: str = "QAT") -> pd.DataFrame:
    frames = []
    for code, name in WB_INDICATORS.items():
        url = f"https://api.worldbank.org/v2/country/{country}/indicator/{code}"
        resp = requests.get(url, params={"format": "json", "per_page": 200}, timeout=30)
        resp.raise_for_status()
        rows = resp.json()[1] or []
        frames.append(pd.DataFrame(
            {"year": [int(r["date"]) for r in rows], name: [r["value"] for r in rows]}
        ).set_index("year"))
    out = pd.concat(frames, axis=1).sort_index()
    out.to_csv(EXT / "world_bank_qatar.csv")
    return out


def fetch_kaggle() -> None:
    slug = os.getenv("KAGGLE_DATASET")
    if not (slug and os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY")):
        print("Kaggle skipped: set KAGGLE_USERNAME, KAGGLE_KEY and KAGGLE_DATASET in .env")
        return
    from kaggle.api.kaggle_api_extended import KaggleApi  # imported late: needs credentials
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(slug, path=str(EXT / "kaggle"), unzip=True)
    print(f"Kaggle dataset {slug} saved to data/external/kaggle")


if __name__ == "__main__":
    print(fetch_world_bank().tail())
    fetch_kaggle()
