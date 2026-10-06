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
    "mortgage_rates_quarterly.csv"
)


def main():

    print("Running mortgage-rate validation...")

    df = pd.read_csv(FILE)

    # --------------------------------------------------
    # 1. Dataset must not be empty
    # --------------------------------------------------

    if df.empty:
        raise ValueError(
            "Mortgage-rate dataset is empty."
        )

    print(f"Rows: {len(df):,}")

    # --------------------------------------------------
    # 2. Required columns
    # --------------------------------------------------

    required_columns = [
        "country_code",
        "country",
        "period",
        "year",
        "quarter",
        "mortgage_rate",
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

    missing_countries = expected - actual

    if missing_countries:

        print(
            "\nWARNING - mortgage data missing for:"
        )

        print(sorted(missing_countries))

    # --------------------------------------------------
    # 4. Duplicate country-quarter observations
    # --------------------------------------------------

    duplicates = df.duplicated(
        [
            "country_code",
            "period",
        ]
    ).sum()

    print(
        f"\nDuplicate country-quarter rows: "
        f"{duplicates}"
    )

    if duplicates > 0:
        raise ValueError(
            f"{duplicates} duplicate mortgage "
            f"observations found."
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
            "Missing values detected "
            "in mortgage dataset."
        )

    # --------------------------------------------------
    # 6. Quarter sanity check
    # --------------------------------------------------

    if not (
        df["quarter"]
        .between(1, 4)
        .all()
    ):
        raise ValueError(
            "Invalid quarter detected."
        )

    # --------------------------------------------------
    # 7. Mortgage-rate sanity check
    # --------------------------------------------------
    #
    # We are not enforcing an arbitrary narrow
    # historical range here. We simply flag
    # unusual observations for inspection.
    # --------------------------------------------------

    unusual = df[
        (df["mortgage_rate"] < -1)
        |
        (df["mortgage_rate"] > 20)
    ]

    print("\nUnusual mortgage-rate observations:")

    if unusual.empty:

        print("None")

    else:

        print(
            unusual[
                [
                    "country",
                    "period",
                    "mortgage_rate",
                ]
            ].to_string(index=False)
        )

        raise ValueError(
            "Mortgage rates outside expected "
            "sanity range detected."
        )

    # --------------------------------------------------
    # 8. Coverage
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

    # --------------------------------------------------
    # 9. Check gaps inside each country's series
    # --------------------------------------------------

    print("\nQuarterly continuity:")

    gaps_found = False

    for country_code, group in df.groupby(
        "country_code"
    ):

        group = group.sort_values(
            [
                "year",
                "quarter",
            ]
        )

        periods = pd.PeriodIndex(
            group["period"],
            freq="Q",
        )

        expected_periods = pd.period_range(
            start=periods.min(),
            end=periods.max(),
            freq="Q",
        )

        missing_periods = (
            expected_periods
            .difference(periods)
        )

        country_name = (
            group["country"].iloc[0]
        )

        if len(missing_periods) == 0:

            print(
                f"{country_name}: "
                f"no gaps"
            )

        else:

            gaps_found = True

            print(
                f"{country_name}: "
                f"missing "
                f"{list(missing_periods)}"
            )

    # --------------------------------------------------
    # 10. Summary statistics
    # --------------------------------------------------

    print("\nMortgage-rate summary:")

    summary = (
        df.groupby("country")
        ["mortgage_rate"]
        .agg(
            [
                "min",
                "max",
                "mean",
            ]
        )
        .round(2)
    )

    print(summary)

    # --------------------------------------------------
    # 11. Latest observations
    # --------------------------------------------------

    latest = (
        df.sort_values(
            [
                "country_code",
                "year",
                "quarter",
            ]
        )
        .groupby("country_code")
        .tail(1)
    )

    print("\nLatest mortgage observations:")

    print(
        latest[
            [
                "country",
                "period",
                "mortgage_rate",
            ]
        ]
        .sort_values("country")
        .to_string(index=False)
    )

    # --------------------------------------------------
    # Success
    # --------------------------------------------------

    if gaps_found:

        print(
            "\nWARNING: At least one mortgage "
            "series contains quarterly gaps."
        )

    print(
        "\nMORTGAGE VALIDATION PASSED"
    )


if __name__ == "__main__":
    main()