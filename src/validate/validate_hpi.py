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
    "house_price_index.csv"
)


def main():

    df = pd.read_csv(FILE)

    print("Running HPI validation...")

    # 1. Countries

    actual_countries = set(
        df["country_code"].unique()
    )

    expected_countries = set(
        COUNTRIES.keys()
    )

    assert actual_countries == expected_countries, (
        f"Country mismatch: {actual_countries}"
    )

    # 2. Duplicate observations

    duplicates = df.duplicated(
        subset=[
            "country_code",
            "period"
        ]
    ).sum()

    assert duplicates == 0, (
        f"{duplicates} duplicate rows found"
    )

    # 3. Missing keys

    assert (
        df["country_code"]
        .notna()
        .all()
    )

    assert (
        df["period"]
        .notna()
        .all()
    )

    # 4. Positive index

    assert (
        df["official_hpi"] > 0
    ).all()

    # 5. Check our baseline

    baseline = (
        df[df["year"] == 2015]
        .groupby("country")["hpi_2015_100"]
        .mean()
    )

    print("\n2015 rebased averages:")
    print(baseline)

    assert (
        (baseline - 100)
        .abs()
        .max()
        < 0.1
    )

    # --------------------------------------------------
    # PERIOD COVERAGE
    # --------------------------------------------------

    print("\nPeriod coverage by country:")

    coverage = (
        df.groupby("country")
        .agg(
            first_period=("period", "min"),
            last_period=("period", "max"),
            observations=("period", "count"),
        )
    )

    print(coverage)


    # --------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------

    missing = df[
        [
            "country_code",
            "period",
            "official_hpi",
            "hpi_2015_100",
        ]
    ].isna().sum()

    print("\nMissing values:")
    print(missing)

    assert missing.sum() == 0, (
        "Missing values detected in HPI dataset"
    )


    # --------------------------------------------------
    # EXPECTED QUARTERS PER YEAR
    # --------------------------------------------------

    quarter_counts = (
        df.groupby(
            ["country_code", "year"]
        )
        ["quarter"]
        .nunique()
    )

    invalid_years = quarter_counts[
        quarter_counts > 4
    ]

    assert invalid_years.empty, (
        "More than four quarters found "
        "for a country-year."
    )

    print("\nHPI VALIDATION PASSED")


if __name__ == "__main__":
    main()