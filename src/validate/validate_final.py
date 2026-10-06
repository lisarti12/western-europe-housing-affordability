import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    COUNTRIES,
    FINAL_DIR,
)


ANNUAL_FILE = (
    FINAL_DIR /
    "fact_affordability_annual.csv"
)

QUARTERLY_FILE = (
    FINAL_DIR /
    "fact_market_quarterly.csv"
)


def validate_annual():

    print("=" * 60)
    print("VALIDATING ANNUAL AFFORDABILITY TABLE")
    print("=" * 60)

    df = pd.read_csv(ANNUAL_FILE)

    print(f"\nRows: {len(df):,}")

    # --------------------------------------------------
    # Countries
    # --------------------------------------------------

    expected = set(COUNTRIES.keys())
    actual = set(df["country_code"].unique())

    assert actual == expected, (
        f"Annual country mismatch: {actual}"
    )

    # --------------------------------------------------
    # Unique country-year
    # --------------------------------------------------

    duplicates = df.duplicated(
        [
            "country_code",
            "year",
        ]
    ).sum()

    print(
        f"Duplicate country-years: {duplicates}"
    )

    assert duplicates == 0

    # --------------------------------------------------
    # Core values cannot be missing
    # --------------------------------------------------

    core_columns = [
        "hpi_2015_100",
        "rent_2015_100",
        "income_per_capita_eur",
        "income_2015_100",
        "hpi_income_gap_pp",
        "rent_income_gap_pp",
    ]

    missing = (
        df[core_columns]
        .isna()
        .sum()
    )

    print("\nMissing core values:")
    print(missing)

    assert missing.sum() == 0

    # --------------------------------------------------
    # 2015 baseline
    # --------------------------------------------------

    baseline = df[
        df["year"] == 2015
    ]

    assert len(baseline) == len(COUNTRIES)

    for column in [
        "hpi_2015_100",
        "rent_2015_100",
        "income_2015_100",
    ]:

        error = (
            baseline[column] - 100
        ).abs().max()

        assert error < 0.1, (
            f"{column} baseline failed."
        )

    # Affordability gaps must begin at zero.

    assert (
        baseline["hpi_income_gap_pp"]
        .abs()
        .max()
        < 0.1
    )

    assert (
        baseline["rent_income_gap_pp"]
        .abs()
        .max()
        < 0.1
    )

    # --------------------------------------------------
    # Complete historical period
    # --------------------------------------------------

    historical = df[
        df["year"].between(
            2015,
            2025,
        )
    ]

    expected_rows = (
        len(COUNTRIES) * 11
    )

    print(
        f"\n2015-2025 rows: "
        f"{len(historical)} "
        f"(expected {expected_rows})"
    )

    assert (
        len(historical)
        == expected_rows
    )

    assert (
        historical[
            "is_complete_year"
        ]
        .all()
    )

    # --------------------------------------------------
    # 2026 should be partial
    # --------------------------------------------------

    partial_2026 = df[
        df["year"] == 2026
    ]

    print(
        f"2026 rows: "
        f"{len(partial_2026)}"
    )

    if not partial_2026.empty:

        assert not (
            partial_2026[
                "is_complete_year"
            ]
            .any()
        )

    # --------------------------------------------------
    # Latest full-year analytical result
    # --------------------------------------------------

    latest = df[
        df["year"] == 2025
    ].copy()

    print("\n2025 affordability snapshot:")

    print(
        latest[
            [
                "country",
                "hpi_income_gap_pp",
                "rent_income_gap_pp",
            ]
        ]
        .sort_values(
            "hpi_income_gap_pp",
            ascending=False,
        )
        .to_string(index=False)
    )

    print(
        "\nANNUAL TABLE VALIDATION PASSED"
    )


def validate_quarterly():

    print("\n")
    print("=" * 60)
    print("VALIDATING QUARTERLY MARKET TABLE")
    print("=" * 60)

    df = pd.read_csv(
        QUARTERLY_FILE
    )

    print(f"\nRows: {len(df):,}")

    # --------------------------------------------------
    # Countries
    # --------------------------------------------------

    expected = set(COUNTRIES.keys())
    actual = set(
        df["country_code"].unique()
    )

    assert actual == expected, (
        f"Quarterly country mismatch: "
        f"{actual}"
    )

    # --------------------------------------------------
    # Unique country-quarter
    # --------------------------------------------------

    duplicates = df.duplicated(
        [
            "country_code",
            "period",
        ]
    ).sum()

    print(
        f"Duplicate country-quarters: "
        f"{duplicates}"
    )

    assert duplicates == 0

    # --------------------------------------------------
    # Core market data
    # --------------------------------------------------

    hpi_missing = (
        df["hpi_2015_100"]
        .isna()
        .sum()
    )

    rent_missing = (
        df["rent_2015_100"]
        .isna()
        .sum()
    )

    mortgage_missing = (
        df["mortgage_rate"]
        .isna()
        .sum()
    )

    print("\nMissing values:")
    print(
        f"HPI: {hpi_missing}"
    )
    print(
        f"Rent: {rent_missing}"
    )
    print(
        f"Mortgage: {mortgage_missing}"
    )

    assert hpi_missing == 0
    assert rent_missing == 0

    # --------------------------------------------------
    # Portugal should explain mortgage missingness
    # --------------------------------------------------

    missing_mortgage = df[
        df["mortgage_rate"].isna()
    ]

    missing_countries = set(
        missing_mortgage[
            "country_code"
        ].unique()
    )

    print(
        "\nCountries with missing "
        "mortgage data:"
    )

    print(
        sorted(missing_countries)
    )

    assert missing_countries == {
        "PT"
    }, (
        "Unexpected mortgage missingness "
        "detected."
    )

    portugal_rows = len(
        df[
            df["country_code"] == "PT"
        ]
    )

    assert (
        mortgage_missing
        == portugal_rows
    )

    # --------------------------------------------------
    # Expected timeline
    # --------------------------------------------------

    coverage = (
        df.groupby("country")
        .agg(
            first_period=(
                "period",
                "min"
            ),
            last_period=(
                "period",
                "max"
            ),
            observations=(
                "period",
                "count"
            ),
        )
    )

    print("\nCoverage:")
    print(coverage)

    assert (
        coverage[
            "first_period"
        ]
        == "2015-Q1"
    ).all()

    assert (
        coverage[
            "last_period"
        ]
        == "2026-Q2"
    ).all()

    assert (
        coverage[
            "observations"
        ]
        == 46
    ).all()

    # --------------------------------------------------
    # 2015 baselines
    # --------------------------------------------------

    baseline = df[
        df["year"] == 2015
    ]

    hpi_baseline = (
        baseline.groupby("country")
        ["hpi_2015_100"]
        .mean()
    )

    rent_baseline = (
        baseline.groupby("country")
        ["rent_2015_100"]
        .mean()
    )

    assert (
        (hpi_baseline - 100)
        .abs()
        .max()
        < 0.1
    )

    assert (
        (rent_baseline - 100)
        .abs()
        .max()
        < 0.1
    )

    # --------------------------------------------------
    # Sanity check mortgage rates
    # --------------------------------------------------

    available_rates = (
        df["mortgage_rate"]
        .dropna()
    )

    assert (
        available_rates >= -1
    ).all()

    assert (
        available_rates <= 20
    ).all()

    print(
        "\nQUARTERLY TABLE VALIDATION PASSED"
    )


def main():

    validate_annual()

    validate_quarterly()

    print("\n")
    print("=" * 60)
    print("ALL FINAL DATA VALIDATION PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()