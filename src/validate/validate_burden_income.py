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
    "housing_burden_income.csv"
)

EXPECTED_GROUPS = [
    "TOTAL",
    "QU1",
    "QU2",
    "QU3",
    "QU4",
    "QU5",
]

EXPECTED_YEARS = list(
    range(2015, 2026)
)


def main():

    print(
        "Validating housing-cost burden "
        "by income quintile..."
    )

    df = pd.read_csv(FILE)

    print(f"\nRows: {len(df):,}")

    # --------------------------------------------------
    # 1. Required columns
    # --------------------------------------------------

    required = [
        "country_code",
        "country",
        "year",
        "income_group_code",
        "income_group",
        "income_group_order",
        "housing_overburden_rate",
    ]

    missing_columns = [
        col
        for col in required
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: "
            f"{missing_columns}"
        )

    # --------------------------------------------------
    # 2. Country coverage
    # --------------------------------------------------

    expected_countries = set(
        COUNTRIES.keys()
    )

    actual_countries = set(
        df["country_code"].unique()
    )

    print("\nCountries:")
    print(sorted(actual_countries))

    if actual_countries != expected_countries:
        raise ValueError(
            "Country coverage mismatch."
        )

    # --------------------------------------------------
    # 3. Duplicate observations
    # --------------------------------------------------

    duplicates = df.duplicated(
        [
            "country_code",
            "year",
            "income_group_code",
        ]
    ).sum()

    print(
        f"\nDuplicate observations: "
        f"{duplicates}"
    )

    if duplicates > 0:
        raise ValueError(
            "Duplicate burden observations found."
        )

    # --------------------------------------------------
    # 4. Missing values inside existing rows
    # --------------------------------------------------

    missing_values = (
        df[required]
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
    # 5. Rate sanity check
    # --------------------------------------------------

    invalid_rates = df[
        (df["housing_overburden_rate"] < 0)
        |
        (df["housing_overburden_rate"] > 100)
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
    # 6. Find missing country/year/group combinations
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
            "income_group_code",
        ],
    )

    actual_keys = df[
        [
            "country_code",
            "year",
            "income_group_code",
        ]
    ]

    missing_combinations = (
        expected_grid
        .merge(
            actual_keys,
            on=[
                "country_code",
                "year",
                "income_group_code",
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
        "income-group combinations:"
    )

    if missing_combinations.empty:

        print("None")

    else:

        missing_combinations[
            "country"
        ] = (
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
                    "income_group_code",
                ]
            ]
            .to_string(index=False)
        )

    # --------------------------------------------------
    # 7. Observations by country/year
    # --------------------------------------------------

    counts = (
        df.groupby(
            [
                "country",
                "year",
            ]
        )
        .size()
        .reset_index(
            name="groups_available"
        )
    )

    incomplete = counts[
        counts["groups_available"]
        != 6
    ]

    print(
        "\nYears with fewer than "
        "6 income groups:"
    )

    if incomplete.empty:

        print("None")

    else:

        print(
            incomplete.to_string(
                index=False
            )
        )

    # --------------------------------------------------
    # 8. Latest-year snapshot
    # --------------------------------------------------

    latest_year = df["year"].max()

    print(
        f"\nLatest year: "
        f"{latest_year}"
    )

    latest = df[
        df["year"] == latest_year
    ]

    print(
        "\n2025 housing-cost "
        "overburden rates:"
    )

    latest = latest.sort_values(
        [
            "country",
            "income_group_order",
        ]
    )

    print(
        latest[
            [
                "country",
                "income_group",
                "housing_overburden_rate",
            ]
        ].to_string(index=False)
    )

    # --------------------------------------------------
    # 9. Important:
    # Missing source observations are reported,
    # NOT automatically treated as validation failure.
    # --------------------------------------------------

    print(
        "\nBURDEN INCOME VALIDATION PASSED"
    )

    if not missing_combinations.empty:

        print(
            "\nNOTE: Source dataset contains "
            f"{len(missing_combinations)} "
            "missing combinations."
        )

        print(
            "These observations will remain "
            "missing and will NOT be imputed."
        )


if __name__ == "__main__":
    main()