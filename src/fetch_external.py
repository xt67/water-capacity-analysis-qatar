"""Fetch supplementary Qatar water context from official/public APIs.

Core station analysis remains reproducible offline from the committed 2023 files.
This optional script downloads official Qatar Open Data Portal CSV exports and
World Bank context series. Kaggle remains optional and must be configured with
an explicitly verified dataset slug; no Kaggle dataset is assumed to be valid.

Usage: python src/fetch_external.py [--include-kaggle]
Credentials belong in an untracked .env file, never in source control.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
EXT = ROOT / "data" / "external"
PORTAL = "https://www.data.gov.qa/api/explore/v2.1/catalog/datasets/{dataset_id}/exports/csv"
WORLD_BANK = "https://api.worldbank.org/v2/country/QAT/indicator/{indicator}"
TIMEOUT = 45

# These are distinct inventory classes. They must not automatically be summed
# into the station dataset: some may be included in the national aggregate.
QATAR_DATASETS = {
    "km_reservoirs": "water-storage-in-km-reservoirs-2023",
    "ground_tanks": "water-storage-in-ground-tanks-2023",
    "elevated_tanks": "water-storage-in-elevated-tanks-2023",
    "iwpp_reservoirs": "water-storage-in-iwpp-reservoirs-2023",
    "storage_by_type": "total-water-storage-by-type-2023",
    "total_storage_by_year": "total-water-storage-by-year",
}
WB_INDICATORS = {
    "SP.POP.TOTL": "population",
    "ER.H2O.FWTL.ZS": "freshwater_withdrawal_pct_internal_resources",
    "SH.H2O.SMDW.ZS": "people_using_safely_managed_drinking_water_pct",
}


def fetch_portal(session: requests.Session, key: str, dataset_id: str) -> Path:
    url = PORTAL.format(dataset_id=dataset_id)
    response = session.get(url, params={"lang": "en", "timezone": "Asia/Qatar"}, timeout=TIMEOUT)
    response.raise_for_status()
    # Validate that the endpoint actually returned tabular CSV, not an HTML error.
    content_type = response.headers.get("content-type", "").lower()
    if "text/csv" not in content_type and "octet-stream" not in content_type and not response.text[:200].lower().startswith(('year,', '"year"')):
        raise ValueError(f"Unexpected export content type for {dataset_id}: {content_type}")
    path = EXT / f"qatar_{key}_2023.csv"
    path.write_bytes(response.content)
    # Basic parse validation prevents saving an HTML/empty error page as data.
    frame = pd.read_csv(path)
    if frame.empty or len(frame.columns) < 2:
        path.unlink(missing_ok=True)
        raise ValueError(f"Dataset export was empty or malformed: {dataset_id}")
    print(f"Saved {path.relative_to(ROOT)} ({len(frame)} rows)")
    return path


def fetch_world_bank(session: requests.Session) -> pd.DataFrame:
    frames = []
    for indicator, name in WB_INDICATORS.items():
        response = session.get(WORLD_BANK.format(indicator=indicator),
                               params={"format": "json", "per_page": 100}, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
            print(f"World Bank indicator {indicator}: no observations returned; skipped")
            continue
        rows = payload[1]
        frame = pd.DataFrame({"year": [int(row["date"]) for row in rows],
                              name: [row["value"] for row in rows]}).set_index("year")
        frames.append(frame)
    out = pd.concat(frames, axis=1).sort_index() if frames else pd.DataFrame()
    if not out.empty:
        out.to_csv(EXT / "world_bank_qatar_context.csv")
        print(f"Saved data/external/world_bank_qatar_context.csv ({len(out)} years)")
    return out


def fetch_kaggle() -> None:
    slug = os.getenv("KAGGLE_DATASET", "").strip()
    username, key = os.getenv("KAGGLE_USERNAME"), os.getenv("KAGGLE_KEY")
    if not (slug and username and key):
        print("Kaggle skipped: set KAGGLE_USERNAME, KAGGLE_KEY and a verified KAGGLE_DATASET in .env")
        return
    if slug.count("/") != 1 or any(part in slug for part in ("..", "\\")):
        raise ValueError("KAGGLE_DATASET must be an owner/dataset-slug value")
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    destination = EXT / "kaggle"
    destination.mkdir(parents=True, exist_ok=True)
    api.dataset_download_files(slug, path=str(destination), unzip=True)
    print(f"Downloaded optional Kaggle dataset {slug} to data/external/kaggle")
    print("Review its licence, schema, country coverage, date range and overlap before using it.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-kaggle", action="store_true", help="also download verified Kaggle dataset")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    EXT.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "qatar-water-capacity-analysis/1.0 (research use)"})
    failures = []
    for key, dataset_id in QATAR_DATASETS.items():
        try:
            fetch_portal(session, key, dataset_id)
        except Exception as exc:  # continue to retrieve other independent public sources
            failures.append(f"{dataset_id}: {type(exc).__name__}: {exc}")
    try:
        fetch_world_bank(session)
    except Exception as exc:
        failures.append(f"World Bank: {type(exc).__name__}: {exc}")
    if args.include_kaggle:
        try:
            fetch_kaggle()
        except Exception as exc:
            failures.append(f"Kaggle: {type(exc).__name__}: {exc}")
    if failures:
        print("\nSome optional sources could not be fetched:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
