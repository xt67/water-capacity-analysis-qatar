-- 03_analysis_queries.sql  (PostgreSQL)
-- Note: every station reports 0 non-operating capacity in 2023, so "utilization"
-- is always 100 % and is not used. These queries look at size and concentration.

-- 1. National totals (operational stations)
SELECT COUNT(*)                          AS stations,
       SUM(total_installed_mig)          AS total_mig,
       SUM(total_installed_m3)           AS total_m3,
       ROUND(AVG(total_installed_mig), 1) AS mean_mig,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_installed_mig) AS median_mig
FROM water_station_capacity
WHERE status = 'Operational';

-- 2. Share of national storage per station, with running (Pareto) total
SELECT station_name,
       total_installed_mig,
       ROUND(100.0 * total_installed_m3 / SUM(total_installed_m3) OVER (), 2) AS share_pct,
       ROUND(100.0 * SUM(total_installed_m3) OVER (ORDER BY total_installed_m3 DESC, station_name)
             / SUM(total_installed_m3) OVER (), 2)                            AS cumulative_share_pct,
       RANK() OVER (ORDER BY total_installed_m3 DESC)                         AS capacity_rank
FROM water_station_capacity
WHERE status = 'Operational'
ORDER BY total_installed_m3 DESC, station_name;

-- 3. Mega PRPS vs standard RPS
SELECT station_type,
       COUNT(*)                                                    AS stations,
       SUM(total_installed_mig)                                    AS total_mig,
       ROUND(100.0 * SUM(total_installed_mig)
             / SUM(SUM(total_installed_mig)) OVER (), 1)           AS share_pct
FROM water_station_capacity
WHERE status = 'Operational'
GROUP BY station_type;

-- 4. Size bands (simple SQL version of the ML tiers in src/ml_models.py)
SELECT CASE WHEN total_installed_mig >= 84 THEN '1 Very large (>= 84 MIG)'
            WHEN total_installed_mig >= 18 THEN '2 Large (18-83 MIG)'
            WHEN total_installed_mig >=  4 THEN '3 Small (4-17 MIG)'
            ELSE                                '4 Very small (< 4 MIG)' END AS size_band,
       COUNT(*) AS stations,
       SUM(total_installed_mig) AS total_mig
FROM water_station_capacity
WHERE status = 'Operational'
GROUP BY 1
ORDER BY 1;

-- 5. Stations commissioned in 2023 and stations under upgrade
SELECT station_name, commissioned_on, total_installed_mig, status
FROM water_station_capacity
WHERE commissioned_on IS NOT NULL OR status <> 'Operational'
ORDER BY commissioned_on NULLS LAST;

-- 6. Top 5 stations by installed capacity
SELECT station_name, total_installed_m3
FROM water_station_capacity
ORDER BY total_installed_m3 DESC
LIMIT 5;


-- 7. Reconcile station-level subtotal to the published KAHRAMAA national total
-- Official 2023 annual statistics: 2,417.2 MIG / 10,987,273 m3.
WITH station_total AS (
    SELECT SUM(total_installed_mig) AS station_mig,
           SUM(total_installed_m3) AS station_m3
    FROM water_station_capacity
    WHERE status = 'Operational'
)
SELECT station_mig,
       station_m3,
       2417.2::NUMERIC AS official_national_mig,
       10987273::NUMERIC AS official_national_m3,
       station_mig - 2417.2 AS variance_mig,
       station_m3 - 10987273 AS variance_m3
FROM station_total;
