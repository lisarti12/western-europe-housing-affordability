-- ============================================================
-- Financing shock impact by country
--
-- Compares:
-- Pre-shock:   2019-2021
-- Higher-rate: 2023-2024
--
-- Measures how mortgage rates and HPI growth changed
-- between the two periods.
--
-- Descriptive relationship only — not causal inference.
-- ============================================================

WITH country_periods AS (

    SELECT
        country_code,
        country,

        AVG(
            CASE
                WHEN year BETWEEN 2019 AND 2021
                THEN mortgage_rate
            END
        ) AS pre_mortgage_rate,

        AVG(
            CASE
                WHEN year BETWEEN 2023 AND 2024
                THEN mortgage_rate
            END
        ) AS high_mortgage_rate,

        AVG(
            CASE
                WHEN year BETWEEN 2019 AND 2021
                THEN hpi_yoy_pct
            END
        ) AS pre_hpi_growth,

        AVG(
            CASE
                WHEN year BETWEEN 2023 AND 2024
                THEN hpi_yoy_pct
            END
        ) AS high_hpi_growth

    FROM vw_market_quarterly

    WHERE
        year BETWEEN 2019 AND 2024
        AND mortgage_rate IS NOT NULL

    GROUP BY
        country_code,
        country
)

SELECT
    country_code,
    country,

    ROUND(
        pre_mortgage_rate,
        2
    ) AS pre_mortgage_rate,

    ROUND(
        high_mortgage_rate,
        2
    ) AS high_mortgage_rate,

    ROUND(
        high_mortgage_rate
        - pre_mortgage_rate,
        2
    ) AS mortgage_rate_change_pp,

    ROUND(
        pre_hpi_growth,
        2
    ) AS pre_hpi_growth,

    ROUND(
        high_hpi_growth,
        2
    ) AS high_hpi_growth,

    ROUND(
        high_hpi_growth
        - pre_hpi_growth,
        2
    ) AS hpi_growth_change_pp

FROM country_periods

ORDER BY
    hpi_growth_change_pp;