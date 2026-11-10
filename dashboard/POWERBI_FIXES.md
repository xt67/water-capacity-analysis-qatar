# Power BI correction guide: Qatar water storage (historical 2023 data)

The `.pbix` file is binary and is not edited by the Python pipeline. The current
KPI values 227,273 m³ and 50 MIG identify the Garrafa station, not Qatar's
national total. Correct the measures and use the independent KAHRAMAA national
series as a reconciliation check.

## 1. Model and source

1. Open `water_station_capacity.pbix` in Power BI Desktop.
2. In **Transform data**, point the station table to
   `data/water_stations_qatar_clean.csv` and confirm numeric types for capacity
   columns and Date type for `commissioned_on`.
3. Keep `data_year = 2023`. The internship was performed in **July 2025**;
   do not relabel the historical dataset as 2025.
4. Keep the under-upgrade Old Salwa record available for status analysis, but
   exclude it from operating national totals.

## 2. Create explicit measures

```DAX
Operational Stations =
CALCULATE(
    DISTINCTCOUNT(water_station_capacity[station_name]),
    water_station_capacity[status] = "Operational"
)

Station Installed Capacity (MIG) =
CALCULATE(
    SUM(water_station_capacity[total_installed_mig]),
    water_station_capacity[status] = "Operational"
)

Station Installed Capacity (m3) =
CALCULATE(
    SUM(water_station_capacity[total_installed_m3]),
    water_station_capacity[status] = "Operational"
)

National Storage (MIG, official 2023) = 2417.2
National Storage (m3, official 2023) = 10987273
Station-to-national reconciliation (m3) =
[Station Installed Capacity (m3)] - [National Storage (m3, official 2023)]
```

Use the two `Station Installed Capacity` measures on station-dataset cards.
Use the two `National Storage` measures only when the card is explicitly titled
**Official KAHRAMAA national total (2023)**. Do not mix the station-level subtotal
with the national aggregate as though they are the same measure.

## 3. Official benchmark and reconciliation

KAHRAMAA's 2023 Annual Statistics Report records **10,987,273 m³ / 2,417.2 MIG**
for total water storage. The current 38-station file sums to **10,979,662 m³ /
2,415.53 MIG**, a difference of **7,611 m³ / 1.67 MIG**. This is about 0.07% of
the official national figure. Show this as a reconciliation variance, not as a
silent adjustment to individual stations.

The Open Data Portal separately lists KM reservoirs, IWPP reservoirs, ground
tanks, elevated tanks, towers and total storage by type. Those datasets are
additional context and may overlap the national total. Do not sum them together
until their definitions and inclusion boundaries have been checked.

## 4. Replace visuals

- KPI cards: clearly distinguish **38 operational KM stations subtotal** from
  **official national storage** (10.99M m³ / 2,417.2 MIG).
- Capacity by station: horizontal bar chart, station on Y, installed MIG on X,
  descending sort, data labels off or compact.
- Concentration: Pareto visual with station capacity columns and cumulative
  share line. Use `data/station_clusters.csv[cum_share_pct]` or calculate it
  from the station table.
- Tier mix: use a bar or donut for ML tier capacity share, with a note that tiers
  are descriptive clusters from capacity only.
- Status and station type slicers: `status`, `station_type`.
- Commissioning visual: `commissioned_on`; these dates are not the internship date.

## 5. Interpretation guardrails

- Do not show a utilization KPI: source records contain no reported non-operating
  capacity among the operational stations, so it would misleadingly show 100%.
- Do not label small-capacity stations as operational faults or anomalies.
- The 2023 production capacity comparison is contextual, not a live supply
  adequacy or resilience assessment.

Source: KAHRAMAA Annual Statistics Report 2023, WT25 Total Water Storage 2019–2023:
https://www.km.com.qa/MediaCenter/Publications/SR2023-English.pdf
