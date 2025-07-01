--Utilization Efficiency per Station
SELECT 
  station_name,
  ROUND(operating_mig / NULLIF(total_installed_mig, 0) * 100, 2) AS mig_utilization_percent,
  ROUND(operating_m3 / NULLIF(total_installed_m3, 0) * 100, 2) AS m3_utilization_percent
FROM water_station_capacity;
--Total Installed vs Operating Capacity
SELECT
  SUM(total_installed_m3) AS total_capacity_m3,
  SUM(operating_m3) AS operating_capacity_m3,
  ROUND(SUM(operating_m3) * 100.0 / SUM(total_installed_m3), 2) AS national_utilization_percent
FROM water_station_capacity;
--Stations With Remarks
SELECT station_name, remarks
FROM water_station_capacity
WHERE remarks IS NOT NULL AND TRIM(remarks) <> '';
--stations Commissioned in 2023
SELECT station_name, remarks
FROM water_station_capacity
WHERE remarks ILIKE '%2023%';
--Top 5 Stations by Operating Capacity (M3)
SELECT station_name, operating_m3
FROM water_station_capacity
ORDER BY operating_m3 DESC
LIMIT 5;