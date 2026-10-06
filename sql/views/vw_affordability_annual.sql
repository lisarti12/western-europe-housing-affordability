CREATE OR REPLACE VIEW vw_affordability_annual AS

SELECT
    f.country_code,
    c.country_name AS country,
    f.year,

    f.hpi_2015_100,
    f.rent_2015_100,
    f.income_per_capita_eur,
    f.income_2015_100,

    f.hpi_growth_since_2015_pct,
    f.rent_growth_since_2015_pct,
    f.income_growth_since_2015_pct,

    f.hpi_income_gap_pp,
    f.rent_income_gap_pp,

    f.hpi_yoy_pct,
    f.rent_yoy_pct,
    f.income_yoy_pct,

    f.is_complete_year

FROM fact_affordability_annual f

JOIN dim_country c
    ON f.country_code = c.country_code;