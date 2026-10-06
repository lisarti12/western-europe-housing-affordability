# Methodology

## 1. Objective

The Western Europe Housing Affordability Monitor examines how housing market conditions have changed relative to household incomes across seven Western European countries:

- Belgium
- France
- Germany
- Ireland
- Netherlands
- Portugal
- Spain

The main research question is:

> **Have household incomes kept pace with the cost of housing since 2015?**

The analysis covers 2015–2025 for full-year comparisons. Data from 2026 is retained where available but is treated as partial and excluded from full-year comparisons.

---

## 2. Data Sources

The project uses official data from Eurostat and the European Central Bank (ECB).

### Eurostat

| Dataset | Purpose |
|---|---|
| `prc_hpi_q` | Quarterly House Price Index |
| `prc_hicp_minr` | Monthly HICP actual rentals for housing |
| `nasq_10_nf_tr` | Household disposable income |
| `namq_10_pe` | Population |
| `tessi162` / `ilc_lvho07b` | Housing cost overburden by income quintile |
| `ilc_lvho07d` | Housing cost overburden by degree of urbanisation |

### European Central Bank

ECB Monetary Financial Institution interest-rate statistics are used for country-level mortgage / house-purchase interest rates.

A comparable mortgage-rate series was not available for Portugal within the selected ECB dataset, so Portugal's mortgage-rate observations remain NULL rather than being estimated or substituted.

---

## 3. Data Processing

Data is extracted and processed in Python before being loaded into PostgreSQL.

The general pipeline is:

**Eurostat / ECB → Python → PostgreSQL → SQL → Power BI**

The source datasets have different frequencies, including monthly, quarterly and annual observations.

Rather than forcing all datasets into a single frequency, the project maintains separate annual and quarterly analytical tables.

---

## 4. Baseline and Indexing

2015 is used as the common baseline year.

House prices, rents and disposable income per capita are compared using indices where:

**2015 = 100**

This allows the analysis to compare cumulative growth across variables with different original units.

House Price Index and rent indices measure relative change over time. They do not represent actual property prices or monthly rent amounts.

---

## 5. Disposable Income Per Capita

Household disposable income is taken from Eurostat using:

- Sector: `S14_S15`
- National accounts item: `B6G`
- Direction: `RECV`
- Unit: `CP_MEUR`
- Seasonal adjustment: `SCA`

Population data is used to convert aggregate household disposable income into disposable income per capita.

The resulting annual income-per-capita series is then rebased to 2015 = 100 for comparison with house prices and rents.

All comparisons are nominal. The project does not attempt to convert the series into real, inflation-adjusted values.

---

## 6. House Price–Income Gap

The House Price–Income Gap measures the difference between cumulative house-price growth and cumulative disposable-income-per-capita growth since 2015.

**House Price–Income Gap = HPI Growth Since 2015 − Income Growth Since 2015**

The result is expressed in percentage points.

For example, a gap of +50 percentage points means that cumulative house-price growth has exceeded cumulative income-per-capita growth by 50 percentage points relative to their 2015 baselines.

It should not be interpreted as a direct percentage measure of housing affordability.

---

## 7. Rent–Income Gap

The Rent–Income Gap follows the same approach:

**Rent–Income Gap = Rent Growth Since 2015 − Income Growth Since 2015**

A positive value indicates that rents have grown faster than disposable income per capita since the baseline year.

A negative value indicates that income growth has exceeded rent growth.

---

## 8. Housing Cost Overburden

Eurostat defines the housing cost overburden rate as the percentage of the population living in households where total housing costs represent more than 40% of disposable household income.

The project analyzes this measure across:

- Total population
- Income quintiles
- Cities
- Towns and suburbs
- Rural areas

Income groups are represented using Eurostat's `QU1` through `QU5` classifications.

This provides a different perspective from the market-based indicators because it measures the financial burden experienced by households rather than changes in asset prices.

---

## 9. Mortgage Rates and Market Response

Quarterly mortgage-rate data is compared with House Price Index growth to examine how housing markets behaved as borrowing costs changed.

The analysis compares:

- **Pre-shock period:** 2019–2021
- **Higher-rate period:** 2023–2024

The analysis is descriptive.

Changes in mortgage rates and house-price growth occurring during the same period should not be interpreted as proof that interest rates caused a particular housing-market outcome.

---

## 10. Missing and Incomplete Data

Missing observations are kept as missing rather than artificially filled where doing so could create misleading results.

Notable cases include:

- Portugal has no comparable mortgage-rate observations in the selected ECB series.
- France is missing housing-overburden observations for 2021.
- 2026 contains partial-year observations.

No forward-filling is used to convert annual housing-burden observations into quarterly data.

For full-year comparisons and headline dashboard metrics, 2025 is therefore treated as the latest complete year.

---

## 11. Interpretation

The project intentionally avoids creating a single composite "affordability score."

Housing affordability can appear different depending on the measure being examined.

For example, a country may experience strong house-price growth relative to income without having the highest current housing-cost overburden. Conversely, households may experience significant housing pressure even where house prices have not diverged substantially from income.

The indicators are therefore intended to be interpreted together rather than as substitutes for one another.

---

## 12. Limitations

The analysis has several limitations:

- National averages can hide substantial regional and city-level differences.
- House Price Index values measure price changes rather than absolute property prices.
- Rent indices measure changes rather than actual monthly rents.
- Income comparisons are nominal rather than inflation-adjusted.
- Mortgage-rate coverage is incomplete for Portugal.
- Housing affordability is influenced by factors not included in the model, such as housing supply, taxation, household debt, lending standards and local housing policies.
- Relationships observed between mortgage rates and housing-market performance are descriptive and should not be interpreted as causal.