import sys
from pathlib import Path
import itertools

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    COUNTRIES,
    PROCESSED_DIR,
)


FILE = (
    PROCESSED_DIR /
    "housing_burden_urban.csv"
)

# These are the three categories we actually
# expect for the urbanisation analysis.
EXPECTED_GROUPS = [
    "DEG1",
    "DEG2",
    "DEG3",
]

EXPECTED_YEARS = list(
    range(2015, 2026)
)


def main():

    print(
        "Validating housing-cost burden "
        "by degree of urbanisation..."
    )

    df = pd.read_csv(FILE)

    print(f"\nTotal rows: {len(df):,}")

    # --------------------------------------------------
    # 1. Required columns
    # --------------------------------------------------

    required = [
        "country_code",
        "country",
        "year",
        "urbanisation_code",
        "urbanisation_group",
        "urbanisation_order",
        "housing_overburden_rate",
    ]

    missing_columns = [
        col
        for col in required
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # --------------------------------------------------
    # 2. Separate analytical categories from TOTAL
    # --------------------------------------------------

    analytical = df[
        df["urbanisation_code"].isin(
            EXPECTED_GROUPS
        )
    ].copy()

    total_rows = df[
        df["urbanisation_code"] == "TOTAL"
    ].copy()

    print(
        f"Analytical DEG1-DEG3 rows: "
        f"{len(analytical):,}"
    )

    print(
        f"TOTAL rows: "
        f"{len(total_rows):,}"
    )

    # --------------------------------------------------
    # 3. Show unusual TOTAL rows
    # --------------------------------------------------

    print("\nTOTAL rows found in source:")

    if total_rows.empty:

        print("None")

    else:

        print(
            total_rows[
                [
                    "country",
                    "year",
                    "housing_overburden_rate",
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------
    # 4. Country coverage
    # --------------------------------------------------

    actual_countries = set(
        analytical["country_code"].unique()
    )

    expected_countries = set(
        COUNTRIES.keys()
    )

    print("\nCountries:")
    print(sorted(actual_countries))

    if actual_countries != expected_countries:
        raise ValueError(
            "Country coverage mismatch."
        )

    # --------------------------------------------------
    # 5. Duplicate observations
    # --------------------------------------------------

    duplicates = analytical.duplicated(
        [
            "country_code",
            "year",
            "urbanisation_code",
        ]
    ).sum()

    print(
        f"\nDuplicate analytical "
        f"observations: {duplicates}"
    )

    if duplicates > 0:
        raise ValueError(
            "Duplicate urbanisation "
            "observations found."
        )

    # --------------------------------------------------
    # 6. Null values
    # --------------------------------------------------

    missing_values = (
        analytical[
            [
                "country_code",
                "country",
                "year",
                "urbanisation_code",
                "urbanisation_group",
                "urbanisation_order",
                "housing_overburden_rate",
            ]
        ]
        .isna()
        .sum()
    )

    print("\nMissing values inside rows:")
    print(missing_values)

    if missing_values.sum() > 0:
        raise ValueError(
            "Null values detected."
        )

    # --------------------------------------------------
    # 7. Percentage sanity check
    # --------------------------------------------------

    invalid_rates = analytical[
        (analytical["housing_overburden_rate"] < 0)
        |
        (analytical["housing_overburden_rate"] > 100)
    ]

    print(
        f"\nRates outside 0-100: "
        f"{len(invalid_rates)}"
    )

    if not invalid_rates.empty:
        raise ValueError(
            "Invalid percentage detected."
        )

    # --------------------------------------------------
    # 8. Build expected analytical grid
    # --------------------------------------------------

    expected_grid = pd.DataFrame(
        itertools.product(
            COUNTRIES.keys(),
            EXPECTED_YEARS,
            EXPECTED_GROUPS,
        ),
        columns=[
            "country_code",
            "year",
            "urbanisation_code",
        ],
    )

    actual_keys = analytical[
        [
            "country_code",
            "year",
            "urbanisation_code",
        ]
    ]

    missing_combinations = (
        expected_grid
        .merge(
            actual_keys,
            on=[
                "country_code",
                "year",
                "urbanisation_code",
            ],
            how="left",
            indicator=True,
        )
    )

    missing_combinations = (
        missing_combinations[
            missing_combinations["_merge"]
            == "left_only"
        ]
        .drop(columns="_merge")
    )

    print(
        "\nMissing country/year/"
        "urbanisation combinations:"
    )

    if missing_combinations.empty:

        print("None")

    else:

        missing_combinations["country"] = (
            missing_combinations[
                "country_code"
            ]
            .map(COUNTRIES)
        )

        print(
            missing_combinations[
                [
                    "country",
                    "year",
                    "urbanisation_code",
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------
    # 9. Complete observations by country
    # --------------------------------------------------

    print(
        "\nAnalytical observations "
        "by country:"
    )

    coverage = (
        analytical
        .groupby("country")
        .agg(
            first_year=("year", "min"),
            last_year=("year", "max"),
            observations=(
                "housing_overburden_rate",
                "count",
            ),
        )
    )

    print(coverage)

    # --------------------------------------------------
    # 10. Latest-year snapshot
    # --------------------------------------------------

    latest_year = analytical["year"].max()

    latest = analytical[
        analytical["year"] == latest_year
    ].copy()

    latest = latest.sort_values(
        [
            "country",
            "urbanisation_order",
        ]
    )

    print(
        f"\n{latest_year} housing-cost "
        "overburden by urbanisation:"
    )

    print(
        latest[
            [
                "country",
                "urbanisation_group",
                "housing_overburden_rate",
            ]
        ].to_string(index=False)
    )

    # --------------------------------------------------
    # 11. Result
    # --------------------------------------------------

    print(
        "\nBURDEN URBAN VALIDATION PASSED"
    )

    if not missing_combinations.empty:

        print(
            "\nNOTE: Source dataset contains "
            f"{len(missing_combinations)} "
            "missing analytical combinations."
        )

        print(
            "These observations will remain "
            "missing and will NOT be imputed."
        )

    if not total_rows.empty:

        print(
            "\nNOTE: TOTAL observations are "
            "present in the source but are not "
            "part of the DEG1-DEG3 analytical grid."
        )


if __name__ == "__main__":
    main()