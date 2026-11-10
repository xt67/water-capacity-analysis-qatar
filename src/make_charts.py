"""Static PNG charts (matplotlib) + one interactive HTML dashboard (plotly).

Run ``python src/build_dataset.py`` and ``python src/ml_models.py`` first.
Context figures (clearly sourced in README): Qatar production capacity of
537 MIGD (Kahramaa, via The Peninsula, 25 Feb 2024) and the 2,400 MIG storage
target announced in 2015 for the Water Security Mega Reservoirs programme.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parent.parent
CH = ROOT / "charts"
CH.mkdir(exist_ok=True)
PRODUCTION_MIGD = 537        # context: national production capacity (2023)
STORAGE_TARGET_MIG = 2400    # context: programme target

TIER_COLORS = {"Very large": "#0b3c5d", "Large": "#328cc1",
               "Small": "#8fc1e3", "Very small": "#d9e6f2"}
TIER_ORDER = ["Very large", "Large", "Small", "Very small"]

df = pd.read_csv(ROOT / "data" / "water_stations_qatar_clean.csv")
cl = pd.read_csv(ROOT / "data" / "station_clusters.csv")
ml = json.loads((ROOT / "data" / "ml_summary.json").read_text())
op = cl.sort_values("total_installed_mig", ascending=False).reset_index(drop=True)
total_mig = op["total_installed_mig"].sum()
total_m3 = op["total_installed_m3"].sum()
cover_days = total_mig / PRODUCTION_MIGD

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(CH / name, dpi=160)
    plt.close(fig)


# 1. ranked capacity by station, colored by ML tier -------------------------------
fig, ax = plt.subplots(figsize=(9, 9))
r = op.iloc[::-1]
ax.barh(r["station_name"], r["total_installed_mig"], color=r["tier"].map(TIER_COLORS))
ax.set_xlabel("Installed storage capacity (MIG)")
ax.set_title("Installed reservoir capacity by station, 2023 (colored by ML tier)", loc="left")
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=TIER_COLORS[t]) for t in TIER_ORDER],
          labels=TIER_ORDER, title="K-Means tier", loc="lower right", frameon=False)
save(fig, "01_capacity_by_station.png")

# 2. Pareto ------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(range(len(op)), op["total_installed_mig"], color="#328cc1")
ax.set_xticks(range(len(op)))
ax.set_xticklabels(op["station_name"], rotation=75, ha="right", fontsize=7)
ax.set_ylabel("Capacity (MIG)")
ax2 = ax.twinx()
ax2.plot(range(len(op)), op["cum_share_pct"], color="#d1495b", marker="o", ms=3)
ax2.axhline(80, ls="--", lw=0.8, color="grey")
ax2.set_ylim(0, 105)
ax2.set_ylabel("Cumulative share (%)")
ax2.spines["right"].set_visible(True)
n80 = int((op["cum_share_pct"] < 80).sum() + 1)
ax.set_title(f"Pareto: {n80} of {len(op)} stations hold 80% of national storage", loc="left")
save(fig, "02_pareto.png")

# 3. Lorenz curve ------------------------------------------------------------------
v = np.sort(op["total_installed_m3"].to_numpy())
lor = np.insert(np.cumsum(v) / v.sum(), 0, 0)
x = np.linspace(0, 1, len(lor))
fig, ax = plt.subplots(figsize=(5.5, 5.5))
ax.plot(x, lor, color="#0b3c5d", lw=2, label="Stations")
ax.plot([0, 1], [0, 1], "--", color="grey", label="Perfect equality")
ax.fill_between(x, lor, x, color="#8fc1e3", alpha=0.4)
ax.set_xlabel("Cumulative share of stations")
ax.set_ylabel("Cumulative share of capacity")
ax.set_title(f"Concentration of storage (Gini = {ml['gini']})", loc="left")
ax.legend(frameon=False)
save(fig, "03_lorenz_curve.png")

# 4. tier: share of stations vs share of capacity ----------------------------------
t = op.groupby("tier").agg(stations=("station_name", "count"),
                           capacity=("total_installed_m3", "sum")).reindex(TIER_ORDER)
t["st_pct"] = t["stations"] / t["stations"].sum() * 100
t["cap_pct"] = t["capacity"] / t["capacity"].sum() * 100
fig, ax = plt.subplots(figsize=(7, 4.5))
w = 0.38
xi = np.arange(len(t))
ax.bar(xi - w / 2, t["st_pct"], w, label="% of stations", color="#8fc1e3")
ax.bar(xi + w / 2, t["cap_pct"], w, label="% of capacity", color="#0b3c5d")
for i, (a, b) in enumerate(zip(t["st_pct"], t["cap_pct"])):
    ax.text(i - w / 2, a + 1, f"{a:.0f}%", ha="center", fontsize=8)
    ax.text(i + w / 2, b + 1, f"{b:.0f}%", ha="center", fontsize=8)
ax.set_xticks(xi)
ax.set_xticklabels(t.index)
ax.set_ylabel("%")
ax.set_title("Few big stations, most of the storage", loc="left")
ax.legend(frameon=False)
save(fig, "04_tier_share.png")

# 5. Mega PRPS vs standard ---------------------------------------------------------
g = op.groupby("station_type")["total_installed_mig"].sum()
fig, ax = plt.subplots(figsize=(7, 2.6))
left = 0
for name, color in [("Mega PRPS", "#0b3c5d"), ("Standard RPS", "#8fc1e3")]:
    ax.barh([0], [g[name]], left=left, color=color, label=f"{name}: {g[name]:,.0f} MIG "
            f"({g[name] / g.sum():.0%})")
    left += g[name]
ax.axvline(STORAGE_TARGET_MIG, color="#d1495b", ls="--")
ax.text(STORAGE_TARGET_MIG, 0.42, " 2,400 MIG target", color="#d1495b", fontsize=8, va="bottom")
ax.set_yticks([])
ax.set_xlabel("MIG")
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.35), ncol=2)
ax.set_title("Installed storage: Mega PRPS vs standard RPS", loc="left")
save(fig, "05_mega_vs_standard.png")

# --- interactive dashboard --------------------------------------------------------
fig = make_subplots(
    rows=2, cols=2, vertical_spacing=0.16, horizontal_spacing=0.1,
    specs=[[{"type": "xy", "rowspan": 2}, {"type": "xy", "secondary_y": True}],
           [None, {"type": "domain"}]],
    subplot_titles=("Capacity by station (MIG)", "Pareto: cumulative share of storage",
                    "Capacity by tier"))
r = op.iloc[::-1]
fig.add_trace(go.Bar(
    y=r["station_name"], x=r["total_installed_mig"], orientation="h",
    marker_color=r["tier"].map(TIER_COLORS), showlegend=False,
    customdata=np.stack([r["total_installed_m3"], r["share_pct"], r["tier"]], axis=-1),
    hovertemplate="<b>%{y}</b><br>%{x:,.1f} MIG<br>%{customdata[0]:,.0f} m³<br>"
                  "%{customdata[1]:.1f}% of national<br>Tier: %{customdata[2]}<extra></extra>"),
    row=1, col=1)
fig.add_trace(go.Bar(x=op["station_name"], y=op["total_installed_mig"],
                     marker_color="#328cc1", name="MIG", showlegend=False), row=1, col=2)
fig.add_trace(go.Scatter(x=op["station_name"], y=op["cum_share_pct"], mode="lines+markers",
                         line_color="#d1495b", name="Cumulative %", showlegend=False),
              row=1, col=2, secondary_y=True)
fig.add_trace(go.Pie(labels=t.index, values=t["capacity"], hole=0.55, sort=False,
                     marker_colors=[TIER_COLORS[i] for i in t.index],
                     textinfo="label+percent"), row=2, col=2)
fig.update_xaxes(tickangle=-60, tickfont_size=8, row=1, col=2)
fig.update_yaxes(tickfont_size=9, row=1, col=1)
fig.update_layout(
    template="simple_white", height=1000, margin=dict(t=190, l=20, r=20, b=40),
    title=dict(text="Qatar Water Reservoir Capacity, 2023 (Kahramaa)", x=0.01, y=0.97),
    showlegend=False,
    annotations=list(fig.layout.annotations) + [
        dict(xref="paper", yref="paper", x=0.01, y=1.12, showarrow=False, xanchor="left",
             align="left", font=dict(size=14),
             text=(f"<b>{total_mig:,.0f} MIG</b> installed ({total_m3 / 1e6:.2f} M m³) · "
                   f"<b>{len(op)}</b> operational stations · "
                   f"<b>{ml['top5_share_pct']}%</b> in top 5 · Gini <b>{ml['gini']}</b> · "
                   f"≈ <b>{cover_days:.1f} days</b> of storage at {PRODUCTION_MIGD} MIGD "
                   f"production"))])
html = fig.to_html(include_plotlyjs="cdn", full_html=True)
(ROOT / "dashboard" / "dashboard.html").write_text(html)
print("charts:", sorted(p.name for p in CH.iterdir()), "| storage cover days:", round(cover_days, 2))
