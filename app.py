"""Qatar water reservoir capacity - minimal Streamlit dashboard.

Run locally:   streamlit run app.py
Data: committed CSV/JSON in data/ (built by src/*.py from KAHRAMAA's 2023 data).
"""
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
ACCENT, MUTED, ALERT = "#0b6e99", "#b8d4e3", "#c0392b"
OFFICIAL_TOTAL_M3, OFFICIAL_TOTAL_MIG = 10_987_273, 2_417.2  # KAHRAMAA Annual Statistics 2023

st.set_page_config(page_title="Qatar Water Storage", page_icon="💧", layout="centered")

st.markdown(
    """
    <style>
      .block-container {max-width: 980px; padding-top: 2.2rem;}
      h1 {font-weight: 600; letter-spacing: -0.02em;}
      [data-testid="stMetricValue"] {font-size: 1.9rem; font-weight: 600;}
      [data-testid="stMetricLabel"] {color: #6b7785;}
      #MainMenu, footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load():
    stations = pd.read_csv(ROOT / "data" / "water_stations_qatar_clean.csv")
    clusters = pd.read_csv(ROOT / "data" / "station_clusters.csv")
    summary = json.loads((ROOT / "data" / "ml_summary.json").read_text())
    return stations, clusters, summary


stations, clusters, summary = load()
op = clusters.sort_values("total_installed_mig", ascending=False).reset_index(drop=True)
total_mig, total_m3 = op["total_installed_mig"].sum(), op["total_installed_m3"].sum()


def style(fig, height):
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=34, b=0), template="plotly_white",
        font=dict(family="sans-serif", size=12, color="#33404d"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0), dragmode=False)
    return fig


# --- header ---------------------------------------------------------------------
st.title("Qatar water storage")
st.caption("Installed reservoir capacity by station · KAHRAMAA data, reporting year 2023")

# --- headline numbers -----------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Installed storage", f"{total_mig:,.0f} MIG")
c2.metric("In cubic metres", f"{total_m3 / 1e6:.2f} M m³")
c3.metric("Operational stations", f"{len(op)}")
c4.metric("Top 5 share", f"{summary['top5_share_pct']:.0f}%")

st.write("")

# --- chart 1: capacity by station -----------------------------------------------
st.subheader("Capacity by station")
show = st.radio("Show", ["Top 10", "Top 20", "All"], horizontal=True, label_visibility="collapsed")
n = {"Top 10": 10, "Top 20": 20, "All": len(op)}[show]
view = op.head(n).iloc[::-1]
fig = go.Figure()
for kind, color in [("Mega PRPS", ACCENT), ("Standard RPS", MUTED)]:
    d = view[view["station_type"] == kind]
    fig.add_bar(y=d["station_name"], x=d["total_installed_mig"], orientation="h", name=kind,
                marker_color=color, hovertemplate="<b>%{y}</b><br>%{x:,.1f} MIG<extra></extra>")
fig.update_xaxes(title="MIG (million imperial gallons)", showgrid=True, gridcolor="#eef2f5")
fig.update_yaxes(title=None, categoryorder="array", categoryarray=list(view["station_name"]))
fig.update_layout(barmode="overlay")
st.plotly_chart(style(fig, max(260, 26 * n + 60)), width="stretch",
                config={"displayModeBar": False})

# --- chart 2: concentration -----------------------------------------------------
st.subheader("Concentration")
n80 = int((op["cum_share_pct"] < 80).sum() + 1)
st.caption(f"{n80} of {len(op)} stations hold 80% of storage (Gini {summary['gini']:.2f}).")
fig = go.Figure()
fig.add_scatter(x=list(range(1, len(op) + 1)), y=op["cum_share_pct"], mode="lines+markers",
                line=dict(color=ACCENT, width=2.5), marker=dict(size=5),
                customdata=op["station_name"],
                hovertemplate="%{customdata}<br>%{y:.1f}% cumulative<extra></extra>")
fig.add_hline(y=80, line_dash="dot", line_color="#9aa5b1")
fig.update_xaxes(title="Stations, largest first", showgrid=False, range=[1, len(op)])
fig.update_yaxes(title="Cumulative % of storage", range=[0, 102], gridcolor="#eef2f5")
st.plotly_chart(style(fig, 300), width="stretch", config={"displayModeBar": False})

# --- table ----------------------------------------------------------------------
st.subheader("Stations")
f1, f2 = st.columns([2, 1])
query = f1.text_input("Search", placeholder="Station name", label_visibility="collapsed")
kind = f2.selectbox("Type", ["All types", "Mega PRPS", "Standard RPS"], label_visibility="collapsed")
table = stations.copy()
if query:
    table = table[table["station_name"].str.contains(query, case=False, regex=False)]
if kind != "All types":
    table = table[table["station_type"] == kind]
table = table.sort_values("total_installed_mig", ascending=False)
table["commissioned_on"] = table["commissioned_on"].fillna("")
st.dataframe(
    table[["station_name", "station_type", "status", "total_installed_mig",
           "total_installed_m3", "commissioned_on", "remarks"]],
    hide_index=True, width="stretch",
    column_config={
        "station_name": "Station", "station_type": "Type", "status": "Status",
        "total_installed_mig": st.column_config.NumberColumn("MIG", format="%.1f"),
        "total_installed_m3": st.column_config.NumberColumn("m³", format="localized"),
        "commissioned_on": "Commissioned", "remarks": "Remarks"})
st.download_button("Download CSV", table.to_csv(index=False).encode(),
                   "qatar_water_stations.csv", "text/csv")

# --- notes ----------------------------------------------------------------------
with st.expander("About this data"):
    st.markdown(
        f"""
- **Source:** KAHRAMAA *Water Storage in KM Reservoirs 2023* (Qatar Open Data Portal). Reporting
  year is 2023; the analysis was done during a 2025 internship.
- **Station subtotal vs national total:** the {len(op)} operational stations sum to
  {total_mig:,.2f} MIG ({total_m3:,.0f} m³). KAHRAMAA's Annual Statistics Report 2023 gives a
  national total of {OFFICIAL_TOTAL_MIG:,.1f} MIG ({OFFICIAL_TOTAL_M3:,} m³); the
  {OFFICIAL_TOTAL_M3 - total_m3:,.0f} m³ gap (≈0.07%) is storage outside this station file.
- **Old Salwa** is excluded: all its reservoirs were demolished for upgrading.
- **Not shown:** utilisation, because no station reports non-operating capacity (it would read 100%
  everywhere).
- **Mega PRPS** marks the five stations tagged "Mega RPS" in the source remarks.
        """
    )
