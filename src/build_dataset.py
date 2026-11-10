"""Rebuild the clean station dataset from the raw Kahramaa XLSX (2023 data).

Fixes over the original CSV:
  * the file is renamed (it was ``...clean.csv.csv``)
  * Old Salwa is flagged as ``Demolished (upgrade)`` instead of looking like a
    zero-capacity operating station; its null m3 values stay explicit
  * remarks are kept, plus structured columns derived from them
    (station_type, status, commissioned_on)
  * every row is validated: installed = operating + non-operating, and m3
    agrees with MIG at the 4,545.45 m3/MIG factor used in the source sheet
The reporting year stays 2023, as in the source data.
"""
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "water-storage-in-km-reservoirs-2023.xlsx"
OUT = ROOT / "data" / "water_stations_qatar_clean.csv"

M3_PER_MIG = 4545.45  # factor used by the source sheet (1 MIG ~ 4,546 m3 exactly)
DATA_YEAR = 2023

COLS = {
    "Station": "station_name",
    "Total Installed Capacity, MIG": "total_installed_mig",
    "Non-Operating Capacity, MIG": "non_operating_mig",
    "Operating Capacity, MIG": "operating_mig",
    "Total Installed Capacity, M3": "total_installed_m3",
    "Non-Operating Capacity, M3": "non_operating_m3",
    "Operating Capacity, M3": "operating_m3",
    "Remarks": "remarks",
}


def build() -> pd.DataFrame:
    df = pd.read_excel(RAW).rename(columns=COLS)
    df["station_name"] = df["station_name"].str.strip()

    # --- status / type / commissioning date derived from the remarks ----------
    remarks = df["remarks"].fillna("").str.strip()
    df["status"] = "Operational"
    df.loc[remarks.str.contains("demolished", case=False), "status"] = "Demolished (upgrade)"
    df["station_type"] = "Standard RPS"
    df.loc[remarks.eq("Mega RPS"), "station_type"] = "Mega PRPS"

    def commissioned(text: str):
        m = re.search(r"commissioned on (\d{2})\.(\d{2})\.(\d{4})", text)
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None

    df["commissioned_on"] = remarks.map(commissioned)
    df["remarks"] = remarks.replace("", "No remarks")

    # --- numeric repair: only where a value is derivable, never invented ------
    # Old Salwa has 0 MIG and null m3: 0 MIG == 0 m3.
    for mig, m3 in [
        ("total_installed_mig", "total_installed_m3"),
        ("non_operating_mig", "non_operating_m3"),
        ("operating_mig", "operating_m3"),
    ]:
        df.loc[df[m3].isna() & (df[mig] == 0), m3] = 0.0

    df["data_year"] = DATA_YEAR
    return df


def validate(df: pd.DataFrame) -> None:
    assert df["station_name"].is_unique, "duplicate station names"
    assert df.drop(columns=["commissioned_on"]).isna().sum().sum() == 0, "unexpected nulls"
    inst_gap = (df.total_installed_mig - df.operating_mig - df.non_operating_mig).abs()
    assert (inst_gap < 1e-9).all(), "installed != operating + non-operating (MIG)"
    inst_gap_m3 = (df.total_installed_m3 - df.operating_m3 - df.non_operating_m3).abs()
    assert (inst_gap_m3 < 1).all(), "installed != operating + non-operating (m3)"
    # MIG values are rounded in the source (e.g. Small & Medium: 7.97 MIG vs
    # 36,209 m3 = 7.966 MIG), so compare with a 0.1% relative tolerance.
    expected = df.total_installed_mig * M3_PER_MIG
    rel = ((expected - df.total_installed_m3).abs() / expected.where(expected > 0, 1)).max()
    assert rel < 0.001, f"MIG->m3 conversion off by {rel:.4%}"
    print(f"validation passed: {len(df)} stations, max MIG->m3 relative gap {rel:.4%}")


if __name__ == "__main__":
    data = build()
    validate(data)
    data.to_csv(OUT, index=False)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(data.groupby("status")["total_installed_mig"].agg(["count", "sum"]))
