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
    "rent_index_quarterly.csv"
)


def main():

    df = pd.read_csv(FILE)

    print("Running rent validation...")

    if df.empty:
        raise ValueError(
            "Rent dataset is empty."
        )

    expected = set(COUNTRIES.keys())
    actual = set(df["country_code"].unique())

    if actual != expected:

        print(
            "\nWARNING: Country coverage differs."
        )

        print("Expected:", expected)
        print("Actual:", actual)

    duplicates = df.duplicated(
        [
            "country_code",
            "period",
        ]
    ).sum()

    if duplicates:
        raise ValueError(
            f"{duplicates} duplicate observations."
        )

    missing = df[
        [
            "country_code",
            "period",
            "official_rent_index",
            "rent_2015_100",
        ]
    ].isna().sum()

    print("\nMissing:")
    print(missing)

    if missing.sum() > 0:
        raise ValueError(
            "Missing core rent observations."
        )

    baseline = (
        df[df["year"] == 2015]
        .groupby("country")
        ["rent_2015_100"]
        .mean()
    )

    print("\n2015 baseline:")
    print(baseline)

    if (baseline - 100).abs().max() >= 0.1:
        raise ValueError(
            "2015 rent rebasing failed."
        )

    print("\nCoverage:")

    print(
        df.groupby("country")
        .agg(
            first_period=("period", "min"),
            last_period=("period", "max"),
            observations=("period", "count"),
        )
    )

    print("\nRENT VALIDATION PASSED")


if __name__ == "__main__":
    main()
    