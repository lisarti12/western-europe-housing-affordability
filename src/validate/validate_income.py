import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    COUNTRIES,
    PROCESSED_DIR,
)


FILE = (
    PROCESSED_DIR /
    "income_annual.csv"
)


def main():

    print("Running income validation...")

    df = pd.read_csv(FILE)

    # --------------------------------------------------
    # 1. Dataset exists and is not empty
    # --------------------------------------------------

    if df.empty:
        raise ValueError(
            "Income dataset is empty."
        )

    print(f"Rows: {len(df):,}")

    # --------------------------------------------------
    # 2. Required columns
    # --------------------------------------------------

    required_columns = [
        "country_code",
        "country",
        "year",
        "income_per_capita_eur",
        "income_2015_100",
        "quarters_available",
        "is_full_year",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{missing_columns}"
        )

    # --------------------------------------------------
    # 3. Country coverage
    # --------------------------------------------------

    expected = set(COUNTRIES.keys())

    actual = set(
        df["country_code"].unique()
    )

    print("\nCountries found:")
    print(sorted(actual))

    if actual != expected:
        raise ValueError(
            f"Country mismatch.\n"
            f"Expected: {expected}\n"
            f"Actual: {actual}"
        )

    # --------------------------------------------------
    # 4. Duplicate country-year rows
    # --------------------------------------------------

    duplicates = df.duplicated(
        [
            "country_code",
            "year",
        ]
    ).sum()

    print(
        f"\nDuplicate country-years: "
        f"{duplicates}"
    )

    if duplicates > 0:
        raise ValueError(
            f"{duplicates} duplicate "
            f"country-year rows found."
        )

    # --------------------------------------------------
    # 5. Missing values
    # --------------------------------------------------

    missing = (
        df[required_columns]
        .isna()
        .sum()
    )

    print("\nMissing values:")
    print(missing)

    if missing.sum() > 0:
        raise ValueError(
            "Missing values detected."
        )

    # --------------------------------------------------
    # 6. Positive income values
    # --------------------------------------------------

    if not (
        df["income_per_capita_eur"] > 0
    ).all():
        raise ValueError(
            "Non-positive per-capita "
            "income detected."
        )

    if not (
        df["income_2015_100"] > 0
    ).all():
        raise ValueError(
            "Non-positive income "
            "index detected."
        )

    # --------------------------------------------------
    # 7. Quarter-count sanity check
    # --------------------------------------------------

    valid_quarters = (
        df["quarters_available"]
        .between(1, 4)
        .all()
    )

    if not valid_quarters:
        raise ValueError(
            "Invalid quarters_available "
            "value detected."
        )

    # Full-year flag must correspond to four quarters.
    expected_full_year = (
        df["quarters_available"] == 4
    )

    actual_full_year = (
        df["is_full_year"]
        .astype(str)
        .str.lower()
        .map(
            {
                "true": True,
                "false": False,
            }
        )
    )

    if actual_full_year.isna().any():
        raise ValueError(
            "Invalid is_full_year values."
        )

    if not (
        expected_full_year
        == actual_full_year
    ).all():
        raise ValueError(
            "is_full_year does not match "
            "quarters_available."
        )

    # --------------------------------------------------
    # 8. Validate 2015 = 100
    # --------------------------------------------------

    baseline = (
        df[
            df["year"] == 2015
        ]
        .set_index("country")
        ["income_2015_100"]
    )

    print("\n2015 baseline:")
    print(baseline)

    if len(baseline) != len(COUNTRIES):
        raise ValueError(
            "Not every country has "
            "a 2015 baseline."
        )

    baseline_error = (
        baseline - 100
    ).abs().max()

    if baseline_error >= 0.1:
        raise ValueError(
            "2015 income rebasing failed."
        )

    # --------------------------------------------------
    # 9. Historical full-year coverage
    # --------------------------------------------------

    historical = df[
        df["year"] <= 2025
    ]

    incomplete_historical = historical[
        historical["quarters_available"] != 4
    ]

    print(
        "\nIncomplete observations "
        "through 2025:"
    )

    if incomplete_historical.empty:
        print("None")
    else:
        print(
            incomplete_historical[
                [
                    "country",
                    "year",
                    "quarters_available",
                ]
            ].to_string(index=False)
        )

        raise ValueError(
            "Incomplete historical annual "
            "income observations detected."
        )

    # --------------------------------------------------
    # 10. Report partial/latest observations
    # --------------------------------------------------

    incomplete = df[
        df["quarters_available"] < 4
    ]

    print("\nPartial-year observations:")

    if incomplete.empty:
        print("None")
    else:
        print(
            incomplete[
                [
                    "country",
                    "year",
                    "quarters_available",
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------
    # 11. Coverage
    # --------------------------------------------------

    coverage = (
        df.groupby("country")
        .agg(
            first_year=("year", "min"),
            last_year=("year", "max"),
            observations=("year", "count"),
        )
    )

    print("\nCoverage:")
    print(coverage)

    # --------------------------------------------------
    # 12. Latest FULL-YEAR values
    # --------------------------------------------------

    full_year = df[
        actual_full_year
    ].copy()

    latest_full = (
        full_year
        .sort_values(
            [
                "country_code",
                "year",
            ]
        )
        .groupby("country_code")
        .tail(1)
    )

    print("\nLatest full-year income:")

    print(
        latest_full[
            [
                "country",
                "year",
                "income_per_capita_eur",
                "income_2015_100",
            ]
        ].to_string(index=False)
    )

    # --------------------------------------------------
    # Success
    # --------------------------------------------------

    print(
        "\nINCOME VALIDATION PASSED"
    )


if __name__ == "__main__":
    main()