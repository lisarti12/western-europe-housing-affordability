import sys
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# PROJECT SETUP
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT))


from src.config import (
    COUNTRIES,
    EUROSTAT_RAW_DIR,
    PROCESSED_DIR,
)


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

INPUT_FILE = (
    EUROSTAT_RAW_DIR /
    "house_price_index_raw.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "house_price_index.csv"
)


# --------------------------------------------------
# EUROSTAT FILTERS
# --------------------------------------------------

# I25_Q = quarterly House Price Index
# using Eurostat's current 2025 reference base.

INDEX_UNIT = "I25_Q"

# TOTAL = all dwelling purchases,
# rather than only new or existing dwellings.

TOTAL_DWELLINGS = "TOTAL"


def main():

    print("Reading raw HPI data...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Raw rows: {len(df):,}")

    # --------------------------------------------------
    # 1. INSPECT SOURCE CATEGORIES
    # --------------------------------------------------

    print("\nAvailable units:")
    print(df["unit"].value_counts())

    print("\nAvailable purchase categories:")
    print(df["purchase"].value_counts())


    # --------------------------------------------------
    # 2. FILTER TO THE SERIES WE ACTUALLY NEED
    # --------------------------------------------------

    df = df[
        (df["unit"] == INDEX_UNIT)
        &
        (df["purchase"] == TOTAL_DWELLINGS)
    ].copy()

    print(
        f"\nRows after HPI filtering: {len(df):,}"
    )

    # Fail immediately if our filter becomes invalid
    # after a future Eurostat classification change.

    if df.empty:
        raise ValueError(
            "HPI filtering returned zero rows. "
            "Check Eurostat unit and purchase codes."
        )


    # --------------------------------------------------
    # 3. ADD HUMAN-READABLE COUNTRY NAME
    # --------------------------------------------------

    df["country"] = (
        df["geo"]
        .map(COUNTRIES)
    )


    # --------------------------------------------------
    # 4. PARSE TIME INFORMATION
    # --------------------------------------------------

    df["year"] = (
        df["time"]
        .str[:4]
        .astype(int)
    )

    df["quarter"] = (
        df["time"]
        .str.extract(r"Q(\d)")
        .astype(int)
    )


    # --------------------------------------------------
    # 5. RENAME SOURCE COLUMNS
    # --------------------------------------------------

    df = df.rename(
        columns={
            "geo": "country_code",
            "time": "period",
            "value": "official_hpi",
        }
    )


    # --------------------------------------------------
    # 6. CALCULATE 2015 BASELINE
    # --------------------------------------------------

    baseline = (
        df[df["year"] == 2015]
        .groupby("country_code")
        ["official_hpi"]
        .mean()
        .rename("base_2015")
    )

    print("\n2015 official HPI averages:")
    print(baseline)


    # --------------------------------------------------
    # 7. MERGE BASELINE BACK INTO DATA
    # --------------------------------------------------

    df = df.merge(
        baseline,
        on="country_code",
        how="left"
    )


    # --------------------------------------------------
    # 8. REBASE INDEX TO 2015 = 100
    # --------------------------------------------------

    df["hpi_2015_100"] = (
        df["official_hpi"]
        /
        df["base_2015"]
        * 100
    )

    df["hpi_2015_100"] = (
        df["hpi_2015_100"]
        .round(2)
    )


    # --------------------------------------------------
    # 9. KEEP ANALYTICAL COLUMNS
    # --------------------------------------------------

    df = df[
        [
            "country_code",
            "country",
            "period",
            "year",
            "quarter",
            "official_hpi",
            "hpi_2015_100",
        ]
    ]


    # --------------------------------------------------
    # 10. SORT DATA
    # --------------------------------------------------

    df = df.sort_values(
        [
            "country_code",
            "year",
            "quarter",
        ]
    ).reset_index(drop=True)


    # --------------------------------------------------
    # 11. SAVE PROCESSED DATA
    # --------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    # --------------------------------------------------
    # 12. SUMMARY
    # --------------------------------------------------

    print("\nProcessed HPI sample:")
    print(df.head(20))

    print("\nCountries:")
    print(
        df["country"]
        .value_counts()
        .sort_index()
    )

    print("\nPeriod range:")
    print(
        df["period"].min(),
        "→",
        df["period"].max()
    )

    print("\nSaved processed HPI:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()