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


INPUT_FILE = (
    EUROSTAT_RAW_DIR /
    "rent_hicp_raw.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "rent_index_quarterly.csv"
)


# IMPORTANT:
# Confirm these from extract_rent.py output.
INDEX_UNIT = "I25"

# Replace this after inspecting the live ECOICOP categories.
RENT_CATEGORY = "CP041"


def main():

    df = pd.read_csv(INPUT_FILE)

    print("Raw rows:", len(df))

    print("\nAvailable units:")
    print(df["unit"].value_counts())

    print("\nRent classifications:")
    print(df["coicop18"].value_counts().head(50))

    df = df[
        (df["unit"] == INDEX_UNIT)
        &
        (df["coicop18"] == RENT_CATEGORY)
    ].copy()

    if df.empty:
        raise ValueError(
            "Rent filter returned zero rows. "
            "Check INDEX_UNIT and RENT_CATEGORY."
        )

    df["date"] = pd.to_datetime(
        df["time"] + "-01"
    )

    df["year"] = df["date"].dt.year

    df["quarter"] = (
        df["date"].dt.quarter
    )

    df["country"] = (
        df["geo"].map(COUNTRIES)
    )

    # Monthly observations -> quarterly average

    quarterly = (
        df.groupby(
            [
                "geo",
                "country",
                "year",
                "quarter",
            ],
            as_index=False,
        )
        ["value"]
        .mean()
    )

    quarterly = quarterly.rename(
        columns={
            "geo": "country_code",
            "value": "official_rent_index",
        }
    )

    quarterly["period"] = (
        quarterly["year"].astype(str)
        + "-Q"
        + quarterly["quarter"].astype(str)
    )

    # --------------------------------------------------
    # Rebase to 2015 = 100
    # --------------------------------------------------

    base = (
        quarterly[
            quarterly["year"] == 2015
        ]
        .groupby("country_code")
        ["official_rent_index"]
        .mean()
        .rename("base_2015")
    )

    quarterly = quarterly.merge(
        base,
        on="country_code",
        how="left",
    )

    quarterly["rent_2015_100"] = (
        quarterly["official_rent_index"]
        /
        quarterly["base_2015"]
        * 100
    ).round(2)

    quarterly = quarterly[
        [
            "country_code",
            "country",
            "period",
            "year",
            "quarter",
            "official_rent_index",
            "rent_2015_100",
        ]
    ]

    quarterly = quarterly.sort_values(
        [
            "country_code",
            "year",
            "quarter",
        ]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    quarterly.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nProcessed rows:")
    print(len(quarterly))

    print("\nSample:")
    print(quarterly.head(20))

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()