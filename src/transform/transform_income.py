import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))


from src.config import (
    COUNTRIES,
    EUROSTAT_RAW_DIR,
    PROCESSED_DIR,
)


INCOME_FILE = (
    EUROSTAT_RAW_DIR /
    "household_income_raw.csv"
)

POPULATION_FILE = (
    PROCESSED_DIR /
    "population_quarterly.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "income_annual.csv"
)


# Eurostat national-accounts income filters
UNIT = "CP_MEUR"
SECTOR = "S14_S15"
NA_ITEM = "B6G"
DIRECTION = "RECV"
SEASONAL_ADJUSTMENT = "SCA"


def main():

    print("Reading raw household income data...")

    income = pd.read_csv(INCOME_FILE)

    print(f"Raw income rows: {len(income):,}")

    # --------------------------------------------------
    # 1. Select gross disposable household income
    # --------------------------------------------------

    income = income[
        (income["unit"] == UNIT)
        & (income["sector"] == SECTOR)
        & (income["na_item"] == NA_ITEM)
        & (income["direct"] == DIRECTION)
        & (income["s_adj"] == SEASONAL_ADJUSTMENT)
    ].copy()

    income = income[
        income["geo"].isin(COUNTRIES.keys())
    ].copy()

    print(
        f"Rows after income filtering: "
        f"{len(income):,}"
    )

    if income.empty:
        raise ValueError(
            "Income filtering returned zero rows."
        )

    # --------------------------------------------------
    # 2. Create quarterly keys
    # --------------------------------------------------

    income["year"] = (
        income["time"]
        .str[:4]
        .astype(int)
    )

    income["quarter"] = (
        income["time"]
        .str.extract(r"Q(\d)")
        .astype(int)
    )

    income["period"] = (
        income["year"].astype(str)
        + "-Q"
        + income["quarter"].astype(str)
    )

    income["country"] = (
        income["geo"].map(COUNTRIES)
    )

    income = income.rename(
        columns={
            "geo": "country_code",
            "value": "disposable_income_meur",
        }
    )

    # --------------------------------------------------
    # 3. Check quarterly uniqueness
    # --------------------------------------------------

    duplicates = income.duplicated(
        [
            "country_code",
            "period",
        ]
    ).sum()

    print(
        f"\nDuplicate income quarters: "
        f"{duplicates}"
    )

    if duplicates > 0:
        raise ValueError(
            f"Found {duplicates} duplicate "
            f"income observations."
        )

    # --------------------------------------------------
    # 4. Load quarterly population
    # --------------------------------------------------

    print("\nReading quarterly population...")

    population = pd.read_csv(
        POPULATION_FILE
    )

    print(
        f"Population rows: "
        f"{len(population):,}"
    )

    # --------------------------------------------------
    # 5. Merge income with population
    # --------------------------------------------------

    income = income.merge(
        population[
            [
                "country_code",
                "period",
                "population",
            ]
        ],
        on=[
            "country_code",
            "period",
        ],
        how="left",
        validate="one_to_one",
    )

    missing_population = (
        income["population"]
        .isna()
        .sum()
    )

    print(
        f"Income rows missing population: "
        f"{missing_population}"
    )

    if missing_population > 0:
        raise ValueError(
            "Some income observations could "
            "not be matched to population."
        )

    # --------------------------------------------------
    # 6. Calculate disposable income per capita
    # --------------------------------------------------
    #
    # Income is expressed in MILLION euros.
    #
    # Example:
    #
    # 60,000 million EUR
    # = 60,000,000,000 EUR
    #
    # Therefore:
    #
    # income per capita =
    # (income in million EUR * 1,000,000)
    # / population
    # --------------------------------------------------

    income["income_per_capita_eur"] = (
        (
            income["disposable_income_meur"]
            * 1_000_000
        )
        /
        income["population"]
    )

    # --------------------------------------------------
    # 7. Inspect quarterly result
    # --------------------------------------------------

    print("\nQuarterly income-per-capita sample:")

    print(
        income[
            [
                "country_code",
                "period",
                "disposable_income_meur",
                "population",
                "income_per_capita_eur",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    # --------------------------------------------------
    # 8. Convert quarterly observations to annual
    # --------------------------------------------------
    #
    # We calculate per-capita income at quarterly level
    # first, then take the annual average.
    # --------------------------------------------------

    annual = (
        income.groupby(
            [
                "country_code",
                "country",
                "year",
            ],
            as_index=False,
        )
        .agg(
            income_per_capita_eur=(
                "income_per_capita_eur",
                "mean",
            ),
            quarters_available=(
                "quarter",
                "count",
            ),
        )
    )

    annual["income_per_capita_eur"] = (
        annual["income_per_capita_eur"]
        .round(2)
    )

    # --------------------------------------------------
    # 9. Rebase income per capita to 2015 = 100
    # --------------------------------------------------

    baseline = (
        annual[
            annual["year"] == 2015
        ]
        .set_index("country_code")
        ["income_per_capita_eur"]
    )

    print("\n2015 per-capita income baseline:")

    print(baseline)

    missing_baselines = (
        set(COUNTRIES.keys())
        - set(baseline.index)
    )

    if missing_baselines:
        raise ValueError(
            "Missing 2015 baseline for: "
            f"{missing_baselines}"
        )

    annual["income_2015_100"] = (
        annual["income_per_capita_eur"]
        /
        annual["country_code"].map(
            baseline
        )
        * 100
    ).round(2)

    # --------------------------------------------------
    # 10. Flag incomplete years
    # --------------------------------------------------

    annual["is_full_year"] = (
        annual["quarters_available"] == 4
    )

    # --------------------------------------------------
    # 11. Final structure
    # --------------------------------------------------

    annual = annual[
        [
            "country_code",
            "country",
            "year",
            "income_per_capita_eur",
            "income_2015_100",
            "quarters_available",
            "is_full_year",
        ]
    ]

    annual = annual.sort_values(
        [
            "country_code",
            "year",
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # 12. Save
    # --------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    annual.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nProcessed annual income:")

    print(
        annual.head(30)
        .to_string(index=False)
    )

    print("\nCoverage:")

    print(
        annual.groupby("country")
        .agg(
            first_year=("year", "min"),
            last_year=("year", "max"),
            observations=("year", "count"),
        )
    )

    print("\nIncomplete annual observations:")

    print(
        annual[
            ~annual["is_full_year"]
        ][
            [
                "country",
                "year",
                "quarters_available",
            ]
        ].to_string(index=False)
    )

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()