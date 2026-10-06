# Data Dictionary

This document describes the analytical datasets used in the Western Europe Housing Affordability Monitor.

---

## `fact_affordability_annual`

Annual country-level affordability indicators.

**Grain:** One row per country per year.

| Column | Description |
|---|---|
| `country_code` | Two-letter country code |
| `country` | Country name |
| `year` | Calendar year |
| `hpi_2015_100` | House Price Index rebased so 2015 = 100 |
| `rent_2015_100` | Rent index rebased so 2015 = 100 |
| `income_per_capita_eur` | Nominal household disposable income per capita in EUR |
| `income_2015_100` | Disposable income per capita rebased so 2015 = 100 |
| `hpi_growth_since_2015_pct` | Cumulative house-price growth relative to the 2015 baseline |
| `rent_growth_since_2015_pct` | Cumulative rent growth relative to the 2015 baseline |
| `income_growth_since_2015_pct` | Cumulative disposable-income-per-capita growth relative to the 2015 baseline |
| `hpi_income_gap_pp` | HPI growth minus income growth, in percentage points |
| `rent_income_gap_pp` | Rent growth minus income growth, in percentage points |
| `hpi_yoy_pct` | Annual year-over-year HPI growth |
| `rent_yoy_pct` | Annual year-over-year rent growth |
| `income_yoy_pct` | Annual year-over-year disposable-income-per-capita growth |
| `is_complete_year` | Indicates whether the year is considered complete for annual comparison |

---

## `fact_market_quarterly`

Quarterly housing-market and financing indicators.

**Grain:** One row per country per quarter.

| Column | Description |
|---|---|
| `country_code` | Two-letter country code |
| `country` | Country name |
| `period` | Quarter identifier, e.g. `2025-Q4` |
| `year` | Calendar year |
| `quarter` | Quarter number from 1 to 4 |
| `hpi_2015_100` | Quarterly House Price Index rebased so 2015 = 100 |
| `rent_2015_100` | Quarterly rent index rebased so 2015 = 100 |
| `mortgage_rate` | Country-level mortgage / house-purchase interest rate |
| `hpi_qoq_pct` | Quarter-over-quarter HPI growth |
| `rent_qoq_pct` | Quarter-over-quarter rent growth |
| `hpi_yoy_pct` | Year-over-year HPI growth |
| `rent_yoy_pct` | Year-over-year rent growth |
| `has_rent_data` | Indicates whether rent data is available for the observation |
| `has_mortgage_data` | Indicates whether mortgage-rate data is available |
| `has_complete_market_data` | Indicates whether all required market indicators are available |

**Note:** Portugal's `mortgage_rate` values are NULL because a comparable series was unavailable in the selected ECB data.

---

## `fact_burden_income`

Housing-cost overburden by income group.

**Grain:** One row per country, year and income group.

The housing cost overburden rate represents the share of people living in households where housing costs exceed 40% of disposable household income.

| Field | Description |
|---|---|
| Country | Country associated with the observation |
| Year | Observation year |
| Income group | Eurostat income-quintile classification |
| Housing overburden rate | Percentage of the population meeting the overburden definition |

### Income Group Codes

| Code | Meaning |
|---|---|
| `TOTAL` | Total population |
| `QU1` | Lowest-income 20% |
| `QU2` | Second income quintile |
| `QU3` | Third income quintile |
| `QU4` | Fourth income quintile |
| `QU5` | Highest-income 20% |

France has no observations for these groups in 2021 in the source data used by the project.

---

## `fact_burden_urban`

Housing-cost overburden by degree of urbanisation.

**Grain:** One row per country, year and urbanisation category.

| Code | Category |
|---|---|
| `DEG1` | Cities |
| `DEG2` | Towns and suburbs |
| `DEG3` | Rural areas |

The primary measure is the housing cost overburden rate, expressed as a percentage.

France has no observations for these categories in 2021 in the source data used by the project.

---

## Country Dimension

The analytical model contains the following seven countries:

| Code | Country |
|---|---|
| `BE` | Belgium |
| `DE` | Germany |
| `ES` | Spain |
| `FR` | France |
| `IE` | Ireland |
| `NL` | Netherlands |
| `PT` | Portugal |

---

## Power BI Dimensions

### `Dim Country`

Provides the shared country filter across all fact tables.

**Relationship:** One-to-many from `Dim Country` to each fact table.

### `Dim Year`

Contains years from 2015 onward and provides a shared year filter across annual, quarterly and housing-burden datasets.

**Relationship:** One-to-many from `Dim Year` to each fact table.

Fact tables are not directly related to one another.

---

## Units and Formatting

Several percentage-based columns are stored using percentage-point values rather than decimal fractions.

For example:

`31.5` represents **31.5%**, not `0.315`.

Similarly:

`101.3` in `hpi_income_gap_pp` represents **101.3 percentage points**.

This distinction is important when importing the data into visualization or analytical software, as applying percentage formatting to these values without conversion would multiply the displayed value by 100.

---

## Missing Values

Missing values are intentionally preserved where reliable source data is unavailable.

They should not automatically be interpreted as zero.

The main known cases are:

- Portugal mortgage-rate data
- France housing-overburden data for 2021
- Partial observations for 2026

No imputation is performed for these cases.