# Fixing `water_station_capacity.pbix`

The `.pbix` is a binary file and was not edited automatically. `dashboard.html` (interactive)
and `../charts/*.png` replace its visuals; to bring the Power BI report in line:

1. **Refresh the source** to `data/water_stations_qatar_clean.csv` (the old `.csv.csv` file was renamed).
2. **KPI cards were wrong.** They showed 227K m³ and 50.00 MIG (a single station, Garrafa). Use
   `Total installed (MIG) = SUM(total_installed_mig)` and the same for m³ so the cards show
   about 2,416 MIG and 10.98 M m³. Filter `status = "Operational"`.
3. **Replace the pie chart** (most slices read 0 %) with a ranked horizontal bar chart of
   `total_installed_mig` by station, sorted descending, with `station_type` or the tier from
   `data/station_clusters.csv` as the colour.
4. **Replace "Count of station by operating capacity"** with a Pareto (column + line using the
   `cum_share_pct` column of `station_clusters.csv`).
5. Add a slicer on `status` and `station_type`, and a card for the `commissioned_on` stations (2023).
