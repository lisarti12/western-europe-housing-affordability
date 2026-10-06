-- ============================================================
-- Housing affordability project
-- Burden fact tables
-- ============================================================


-- ------------------------------------------------------------
-- 1. Housing-cost overburden by income group
-- Grain:
-- one row per country + year + income group
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_burden_income (
    country_code CHAR(2) NOT NULL,
    year INTEGER NOT NULL,

    income_group_code VARCHAR(10) NOT NULL,
    income_group VARCHAR(30) NOT NULL,
    income_group_order INTEGER NOT NULL,

    housing_overburden_rate NUMERIC(10,2) NOT NULL,

    PRIMARY KEY (
        country_code,
        year,
        income_group_code
    ),

    FOREIGN KEY (country_code)
        REFERENCES dim_country(country_code),

    CHECK (
        housing_overburden_rate
        BETWEEN 0 AND 100
    )
);


-- ------------------------------------------------------------
-- 2. Housing-cost overburden by urbanisation
-- Grain:
-- one row per country + year + urbanisation group
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_burden_urban (
    country_code CHAR(2) NOT NULL,
    year INTEGER NOT NULL,

    urbanisation_code VARCHAR(10) NOT NULL,
    urbanisation_group VARCHAR(30) NOT NULL,
    urbanisation_order INTEGER NOT NULL,

    housing_overburden_rate NUMERIC(10,2) NOT NULL,

    PRIMARY KEY (
        country_code,
        year,
        urbanisation_code
    ),

    FOREIGN KEY (country_code)
        REFERENCES dim_country(country_code),

    CHECK (
        housing_overburden_rate
        BETWEEN 0 AND 100
    )
);


-- ------------------------------------------------------------
-- 3. Indexes
-- Useful for year-based dashboard queries
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_burden_income_year
ON fact_burden_income(year);


CREATE INDEX IF NOT EXISTS idx_burden_urban_year
ON fact_burden_urban(year);