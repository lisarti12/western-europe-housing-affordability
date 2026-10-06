# Western Europe Housing Affordability Monitor

An end-to-end Business Intelligence project analyzing how housing affordability has changed across seven Western European countries since 2015.

The project combines **Eurostat and European Central Bank data** with **Python, PostgreSQL, SQL, and Power BI** to examine the relationship between house prices, household income, rents, mortgage rates, and housing-cost burden.

## Research Question

> Which Western European housing markets have experienced the greatest affordability pressure since 2015, and what appears to be driving that pressure?

The analysis covers:

- 🇧🇪 Belgium
- 🇫🇷 France
- 🇩🇪 Germany
- 🇮🇪 Ireland
- 🇳🇱 Netherlands
- 🇵🇹 Portugal
- 🇪🇸 Spain

The main comparison period is **2015–2025**, with partial 2026 data retained where available but excluded from full-year comparisons.

---

## Dashboard

The Power BI report contains three analytical pages.

### 1. Executive Overview

Provides a high-level comparison of housing affordability across the seven markets.

Key metrics include:

- House price growth since 2015
- Disposable income growth
- House Price–Income Gap
- Housing-cost overburden
- Low-income housing burden
- City vs rural housing burden

### 2. Market & Financing

Examines how housing markets responded to changing borrowing conditions, particularly the interest-rate shock beginning in 2022.

The page compares:

- Mortgage rates over time
- House Price Index YoY growth
- Quarterly HPI growth
- Pre-shock vs higher-rate housing performance
- Mortgage rates before and after the rate shock

### 3. Who Bears the Housing Burden?

Examines the distributional side of housing affordability.

It compares:

- Housing burden across income quintiles
- Lowest vs highest-income households over time
- Cities, towns/suburbs, and rural areas
- Low-income housing burden across countries

---

## Key Findings

### Portugal experienced the largest house price–income divergence

Between 2015 and 2025:

- House Price Index growth: **+163.8%**
- Disposable income per capita growth: **+62.5%**
- House Price–Income Gap: **+101.3 percentage points**

This was the largest divergence among the seven countries analyzed.

### Housing-market pressure and household burden are not the same thing

Portugal recorded the largest house price–income divergence, but Germany recorded the highest overall housing-cost overburden rate in 2025.

Germany:

- Overall housing-cost overburden: **11.2%**
- Lowest-income 20%: **31.5%**
- Highest-income 20%: **1.5%**

This demonstrates why affordability cannot be evaluated using house-price growth alone.

### Lower-income households face substantially greater pressure

Housing-cost overburden among the lowest-income 20% in 2025:

| Country | Overburden Rate |
|---|---:|
| Germany | 31.5% |
| Spain | 27.7% |
| Belgium | 23.5% |
| Netherlands | 23.0% |
| France | 22.6% |
| Portugal | 21.4% |
| Ireland | 13.7% |

Across the analyzed markets, housing-cost pressure is strongly concentrated among lower-income households.

### Cities experience greater housing-cost pressure

In 2025, housing-cost overburden was higher in cities than in rural areas in **all seven countries**.

Across the selected countries, the average rates were approximately:

- Cities: **9.5%**
- Towns & suburbs: **6.2%**
- Rural areas: **4.3%**

### The interest-rate shock affected markets differently

Mortgage financing became substantially more expensive after 2022, but house-price responses varied considerably.

Germany's average HPI YoY growth moved from approximately **+8.4% during 2019–2021** to **−4.9% during 2023–2024**.

France also experienced a substantial slowdown.

Spain and Ireland, however, maintained positive house-price growth despite higher borrowing costs.

The results suggest that financing conditions were important, but **interest rates alone do not explain cross-country housing-market outcomes**.

### Ireland stands out on rental pressure

Ireland was the only country in the analysis where cumulative rent growth exceeded disposable income per capita growth between 2015 and 2025.

Its Rent–Income Gap was approximately **+6.2 percentage points**.

---

## Key Metrics

### House Price–Income Gap

The main affordability indicator compares cumulative House Price Index growth with cumulative nominal disposable income per capita growth from their respective 2015 baselines.

```text
House Price–Income Gap =
HPI Growth Since 2015
−
Disposable Income Per Capita Growth Since 2015
```

A positive value means house prices increased faster than disposable income per capita.

This metric should not be interpreted as a direct percentage change in affordability.

### Rent–Income Gap

```text
Rent–Income Gap =
Rent Index Growth Since 2015
−
Disposable Income Per Capita Growth Since 2015
```

### Housing-Cost Overburden

Eurostat defines the housing-cost overburden rate as the share of the population living in households where total housing costs represent more than **40% of disposable household income**.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Data Sources | Eurostat, European Central Bank |
| Extraction | Python, Requests |
| Transformation | Python, Pandas |
| Validation | Python |
| Database | PostgreSQL |
| Data Analysis | SQL |
| Data Model | Power BI |
| Measures | DAX |
| Visualization | Power BI |
| Version Control | Git & GitHub |

---

## Data Pipeline

```text
Eurostat + ECB
      │
      ▼
Python Extraction
      │
      ▼
Raw Data
      │
      ▼
Python Transformation
      │
      ▼
Validation
      │
      ▼
Processed / Final CSVs
      │
      ▼
PostgreSQL
      │
      ▼
Analytical SQL Views
      │
      ▼
Power BI
```

The separation between extraction, transformation, validation, database loading, analysis, and visualization was intentional so that the workflow remains reproducible and auditable.

---

## Project Structure

```text
western-europe-housing-affordability/
│
├── data/
│   ├── raw/
│   │   ├── eurostat/
│   │   └── ecb/
│   ├── processed/
│   └── final/
│
├── src/
│   ├── extract/
│   ├── transform/
│   ├── validate/
│   ├── load/
│   └── analysis/
│
├── sql/
│   ├── ddl/
│   ├── views/
│   └── analysis/
│
├── powerbi/
├── notebooks/
├── screenshots/
│
├── docs/
│   ├── methodology.md
│   └── data_dictionary.md
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Data Sources

### Eurostat

Eurostat provides the majority of the project's housing, income, population, rent, and household-burden indicators.

Key datasets include:

| Dataset | Purpose |
|---|---|
| `prc_hpi_q` | Quarterly House Price Index |
| `prc_hicp_minr` | HICP actual rentals for housing |
| `nasq_10_nf_tr` | Household gross disposable income |
| `namq_10_pe` | Population |
| `ilc_lvho07b` / `tessi162` | Housing-cost overburden by income quintile |
| `ilc_lvho07d` | Housing-cost overburden by degree of urbanisation |

### European Central Bank

ECB Monetary Financial Institution interest-rate statistics were used to analyze country-level mortgage/house-purchase financing conditions.

---

## Data Processing

### House Prices

Quarterly House Price Index observations were rebased so that:

```text
2015 = 100
```

### Rent

Monthly HICP actual-rent observations were aggregated to quarterly frequency and rebased to:

```text
2015 = 100
```

### Disposable Income

Quarterly household and NPISH gross disposable income was converted into disposable income per capita:

```text
Disposable Income Per Capita =
Gross Disposable Income / Population
```

The resulting nominal series was rebased to:

```text
2015 = 100
```

This allows nominal house-price and rent indices to be compared with nominal income growth on a consistent basis.

### Mortgage Rates

Monthly ECB mortgage-rate observations were aggregated to quarterly averages.

### Housing Burden

Annual Eurostat housing-cost overburden data was retained at its natural annual frequency rather than artificially forward-filled into quarterly observations.

---

## PostgreSQL Model

The analytical database contains four primary fact tables:

```text
fact_affordability_annual
fact_market_quarterly
fact_burden_income
fact_burden_urban
```

These connect to a shared country dimension:

```text
dim_country
```

Analytical views used by Power BI include:

```text
vw_affordability_annual
vw_market_quarterly
vw_burden_income
vw_burden_urban
```

This avoids fact-to-fact relationships inside the Power BI model.

---

## Data Quality & Validation

Automated validation scripts check:

- Duplicate country-period observations
- Missing core metrics
- Expected country coverage
- Expected year/quarter coverage
- Baseline values
- Valid percentage ranges
- Partial-year observations
- Missing mortgage observations
- Source-specific missing data

Important known limitations are preserved rather than artificially filled.

For example:

- Comparable ECB mortgage data is unavailable for Portugal in the selected series.
- France has missing housing-burden observations for 2021.
- 2026 contains partial-year observations and is not treated as a complete year.

---

## Limitations

Several limitations should be considered when interpreting the results:

- HPI measures **price change**, not absolute property prices.
- Rent HICP measures **rent change**, not absolute rent levels.
- National averages can hide substantial differences between cities and regions.
- Mortgage structures differ across countries.
- Housing-cost overburden is survey-based.
- Missing observations are not imputed.
- 2026 data is partial.
- Correlations between mortgage rates and housing-market changes should not be interpreted as proof of causation.

The project therefore uses language such as **associated with**, **coincided with**, and **divergence**, rather than making unsupported causal claims.

---

## Main Takeaway

Housing affordability is multidimensional.

A country can experience rapid house-price appreciation without simultaneously having the highest current household housing-cost burden.

The analysis shows three distinct dimensions of housing pressure:

**Market pressure** — house prices relative to income  
**Financing pressure** — the cost of mortgage borrowing  
**Household pressure** — the share of income absorbed by housing costs

Analyzing all three provides a more complete picture than relying on house prices alone.

---

## Author

**Lisart Mella**

Computer Science & Information Systems graduate  
Business Intelligence • Data Analytics • Data Visualization