-- ============================================================
-- Financing conditions around the 2022-2024 rate shock
--
-- Purpose:
-- Compare mortgage rates and house-price growth across countries
-- before and during the higher-rate period.
--
-- IMPORTANT:
-- This is descriptive analysis.
-- It does not establish causality.
-- ============================================================


-- ------------------------------------------------------------
-- 1. Annualise quarterly mortgage rates and HPI
-- ------------------------------------------------------------

WITH annual_market AS (

    SELECT
        country_code,
        country,
        year,

        AVG(mortgage_rate) AS avg_mortgage_rate,

        AVG(hpi_2015_100) AS avg_hpi_index,

        AVG(hpi_yoy_pct) AS avg_hpi_yoy_pct,

        COUNT(mortgage_rate) AS mortgage_quarters_available

    FROM vw_market_quarterly

    WHERE year BETWEEN 2019 AND 2025

    GROUP BY
        country_code,
        country,
        year
)


SELECT
    country_code,
    country,
    year,

    ROUND(
        avg_mortgage_rate,
        2
    ) AS avg_mortgage_rate,

    ROUND(
        avg_hpi_index,
        2
    ) AS avg_hpi_index,

    ROUND(
        avg_hpi_yoy_pct,
        2
    ) AS avg_hpi_yoy_pct,

    mortgage_quarters_available

FROM annual_market

ORDER BY
    country,
    year;