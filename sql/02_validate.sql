-- 02_validate.sql  (PostgreSQL) - run after loading; every query should return 0 rows / expected value.

-- Row count (expect 39: 38 operational + Old Salwa under upgrade)
SELECT COUNT(*) AS stations FROM water_station_capacity;

-- Installed must equal operating + non-operating
SELECT station_name
FROM water_station_capacity
WHERE ABS(total_installed_m3 - operating_m3 - non_operating_m3) >= 1;

-- MIG vs m3 consistency at 4,545.45 m3 per MIG (0.1 % tolerance)
SELECT station_name, total_installed_mig, total_installed_m3
FROM water_station_capacity
WHERE total_installed_mig > 0
  AND ABS(total_installed_mig * 4545.45 - total_installed_m3)
      / (total_installed_mig * 4545.45) > 0.001;

-- Zero-capacity rows must be explained by a status
SELECT station_name
FROM water_station_capacity
WHERE total_installed_mig = 0 AND status = 'Operational';
