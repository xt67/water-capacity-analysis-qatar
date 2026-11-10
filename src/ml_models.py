"""Unsupervised ML on Qatar reservoir-station capacity (2023, n = 38 operational).

Only capacity is available per station, so supervised prediction would be
meaningless (m3 is a fixed multiple of MIG). Instead:
  1. Tiering  - K-Means vs Agglomerative clustering on log-capacity, k picked by
                silhouette score, tiers named by cluster mean capacity.
  2. Outliers - Isolation Forest + robust (MAD) z-score on log-capacity.
  3. Inequality - Lorenz curve / Gini / top-N share of national storage.
Results are written to data/station_clusters.csv and data/ml_summary.json.
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
SEED = 42
TIER_NAMES = {
    2: ["Distribution", "Bulk"],
    3: ["Small", "Medium", "Large"],
    4: ["Very small", "Small", "Large", "Very large"],
    5: ["Very small", "Small", "Medium", "Large", "Very large"],
    6: ["Tiny", "Very small", "Small", "Large", "Very large", "Huge"],
}


def gini(values: np.ndarray) -> float:
    v = np.sort(values)
    n = len(v)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(v) / (n * v.sum()))


def main() -> None:
    df = pd.read_csv(ROOT / "data" / "water_stations_qatar_clean.csv")
    op = df[df["status"] == "Operational"].copy().reset_index(drop=True)
    X = StandardScaler().fit_transform(np.log1p(op[["total_installed_m3"]]))

    # 1. choose k and algorithm by silhouette -----------------------------------
    scores = []
    for k in range(2, 7):
        km = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit(X)
        ag = AgglomerativeClustering(n_clusters=k, linkage="ward").fit(X)
        scores.append({"k": k, "kmeans": silhouette_score(X, km.labels_),
                       "agglomerative": silhouette_score(X, ag.labels_)})
    sc = pd.DataFrame(scores).set_index("k")
    best_k = int(sc["kmeans"].idxmax())
    km = KMeans(n_clusters=best_k, n_init=20, random_state=SEED).fit(X)
    op["cluster"] = km.labels_
    order = op.groupby("cluster")["total_installed_m3"].mean().sort_values().index
    names = TIER_NAMES[best_k]
    op["tier"] = op["cluster"].map({c: names[i] for i, c in enumerate(order)})

    # 2. robust size rarity ------------------------------------------------------
    # This is intentionally NOT called an operational anomaly detector: with
    # capacity alone, it can only identify unusually small/large installations.
    logc = np.log1p(op["total_installed_m3"].astype(float))
    mad = float(np.median(np.abs(logc - logc.median())))
    if mad == 0:
        op["robust_z"] = 0.0
    else:
        op["robust_z"] = 0.6745 * (logc - logc.median()) / mad
    op["size_rarity_flag"] = op["robust_z"].abs() > 3.5
    op["size_rarity_label"] = np.select(
        [op["robust_z"] < -3.5, op["robust_z"] > 3.5],
        ["Unusually small capacity", "Unusually large capacity"],
        default="Within robust size range")

    # 3. concentration ----------------------------------------------------------
    total = op["total_installed_m3"].sum()
    ranked = op.sort_values("total_installed_m3", ascending=False)
    op["share_pct"] = op["total_installed_m3"] / total * 100
    op["cum_share_pct"] = op.sort_values("total_installed_m3", ascending=False)[
        "share_pct"].cumsum()

    summary = {
        "n_stations": int(len(op)),
        "best_k": best_k,
        "silhouette": sc.round(3).to_dict(),
        "tier_counts": op["tier"].value_counts().to_dict(),
        "tier_capacity_share_pct": (op.groupby("tier")["share_pct"].sum().round(1)).to_dict(),
        "gini": round(gini(op["total_installed_m3"].to_numpy()), 3),
        "top5_share_pct": round(ranked["total_installed_m3"].head(5).sum() / total * 100, 1),
        "top10_share_pct": round(ranked["total_installed_m3"].head(10).sum() / total * 100, 1),
        "size_rarity_flags": op.loc[op["size_rarity_flag"], "station_name"].tolist(),
        "interpretation": "Capacity rarity only; not operational faults or failures.",
    }
    out_cols = ["station_name", "total_installed_mig", "total_installed_m3", "station_type",
                "tier", "share_pct", "cum_share_pct", "robust_z",
                "size_rarity_flag", "size_rarity_label"]
    op[out_cols].sort_values("total_installed_m3", ascending=False).round(3).to_csv(
        ROOT / "data" / "station_clusters.csv", index=False)
    (ROOT / "data" / "ml_summary.json").write_text(json.dumps(summary, indent=2))
    print(sc.round(3))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
