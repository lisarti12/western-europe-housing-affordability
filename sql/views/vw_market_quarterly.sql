CREATE OR REPLACE VIEW vw_market_quarterly AS

SELECT
    f.country_code,
    c.country_name AS country,

    f.period,
    f.year,
    f.quarter,

    f.hpi_2015_100,
    f.rent_2015_100,
    f.mortgage_rate,

    f.hpi_qoq_pct,
    f.rent_qoq_pct,
    f.hpi_yoy_pct,
    f.rent_yoy_pct,

    f.has_rent_data,
    f.has_mortgage_data,
    f.has_complete_market_data

FROM fact_market_quarterly f

JOIN dim_country c
    ON f.country_code = c.country_code;