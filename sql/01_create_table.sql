-- 01_create_table.sql  (PostgreSQL)
-- Load data/water_stations_qatar_clean.csv into this table, e.g. in psql:
--   \copy water_station_capacity FROM 'data/water_stations_qatar_clean.csv' CSV HEADER

DROP TABLE IF EXISTS water_station_capacity;

CREATE TABLE water_station_capacity (
    station_name        TEXT PRIMARY KEY,
    total_installed_mig NUMERIC NOT NULL CHECK (total_installed_mig >= 0),
    non_operating_mig   NUMERIC NOT NULL CHECK (non_operating_mig  >= 0),
    operating_mig       NUMERIC NOT NULL CHECK (operating_mig      >= 0),
    total_installed_m3  NUMERIC NOT NULL CHECK (total_installed_m3 >= 0),
    non_operating_m3    NUMERIC NOT NULL CHECK (non_operating_m3   >= 0),
    operating_m3        NUMERIC NOT NULL CHECK (operating_m3       >= 0),
    remarks             TEXT    NOT NULL DEFAULT 'No remarks',
    status              TEXT    NOT NULL,   -- Operational | Demolished (upgrade)
    station_type        TEXT    NOT NULL,   -- Mega PRPS | Standard RPS
    commissioned_on     DATE,               -- only where stated in remarks
    data_year           INT     NOT NULL,   -- reporting year of the source (2023)
    CONSTRAINT capacity_adds_up CHECK (
        abs(total_installed_mig - operating_mig - non_operating_mig) < 0.001)
);
