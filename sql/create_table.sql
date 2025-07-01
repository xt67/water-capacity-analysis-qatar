--create table 
CREATE TABLE water_station_capacity (
    station_name TEXT,
    total_installed_mig NUMERIC,
    non_operating_mig NUMERIC,
    operating_mig NUMERIC,
    total_installed_m3 NUMERIC,
    non_operating_m3 NUMERIC,
    operating_m3 NUMERIC,
    remarks TEXT
);
--view table
select * from water_station_capacity;
--clean table (replace null with no remark in remarks ccolumn)
UPDATE water_station_capacity
SET remarks = 'No remarks'
WHERE remarks IS NULL OR TRIM(remarks) = '';
--clean table (update numeric null values)
UPDATE water_station_capacity
SET 
    total_installed_mig = COALESCE(total_installed_mig, 0),
    non_operating_mig = COALESCE(non_operating_mig, 0),
    operating_mig = COALESCE(operating_mig, 0),
    total_installed_m3 = COALESCE(total_installed_m3, 0),
    non_operating_m3 = COALESCE(non_operating_m3, 0),
    operating_m3 = COALESCE(operating_m3, 0);
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

