-- ============================================================
-- Mortgage rate shock: period comparison
--
-- Pre-shock:       2019-2021
-- Transition:      2022
-- Higher-rate:     2023-2024
-- Latest full year: 2025
--
-- Portugal is excluded because the selected ECB mortgage
-- series has no observations for Portugal.
-- ============================================================

WITH classified AS (

    SELECT
        country_code,
        country,
        year,
        mortgage_rate,
        hpi_yoy_pct,

        CASE
            WHEN year BETWEEN 2019 AND 2021
                THEN 'Pre-shock (2019-2021)'

            WHEN year = 2022
                THEN 'Transition (2022)'

            WHEN year BETWEEN 2023 AND 2024
                THEN 'Higher-rate (2023-2024)'

            WHEN year = 2025
                THEN 'Latest full year (2025)'
        END AS period_group,

        CASE
            WHEN year BETWEEN 2019 AND 2021 THEN 1
            WHEN year = 2022 THEN 2
            WHEN year BETWEEN 2023 AND 2024 THEN 3
            WHEN year = 2025 THEN 4
        END AS period_order

    FROM vw_market_quarterly

    WHERE
        year BETWEEN 2019 AND 2025
        AND mortgage_rate IS NOT NULL
),

summary AS (

    SELECT
        country_code,
        country,
        period_group,
        period_order,

        AVG(mortgage_rate)
            AS avg_mortgage_rate,

        AVG(hpi_yoy_pct)
            AS avg_hpi_yoy_pct,

        COUNT(*)
            AS quarters_used

    FROM classified

    GROUP BY
        country_code,
        country,
        period_group,
        period_order
)

SELECT
    country_code,
    country,
    period_group,

    ROUND(
        avg_mortgage_rate,
        2
    ) AS avg_mortgage_rate,

    ROUND(
        avg_hpi_yoy_pct,
        2
    ) AS avg_hpi_yoy_pct,

    quarters_used

FROM summary

ORDER BY
    country,
    period_order;