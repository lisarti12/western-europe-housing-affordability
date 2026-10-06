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
    "population_raw.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "population_quarterly.csv"
)


UNIT = "THS_PER"
NA_ITEM = "POP_NC"
SEASONAL_ADJUSTMENT = "NSA"


def main():

    print("Reading raw population data...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Raw rows: {len(df):,}")

    # --------------------------------------------------
    # 1. Select the population series we need
    # --------------------------------------------------

    df = df[
        (df["unit"] == UNIT)
        & (df["na_item"] == NA_ITEM)
        & (df["s_adj"] == SEASONAL_ADJUSTMENT)
    ].copy()

    print(
        f"Rows after population filtering: "
        f"{len(df):,}"
    )

    if df.empty:
        raise ValueError(
            "Population filtering returned zero rows."
        )

    # --------------------------------------------------
    # 2. Keep our seven countries
    # --------------------------------------------------

    df = df[
        df["geo"].isin(COUNTRIES.keys())
    ].copy()

    df["country"] = (
        df["geo"].map(COUNTRIES)
    )

    # --------------------------------------------------
    # 3. Extract year and quarter
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
    # 4. Convert thousand persons → persons
    # --------------------------------------------------

    df["population"] = (
        df["value"] * 1000
    ).round(0)

    df["population"] = (
        df["population"]
        .astype("int64")
    )

    # --------------------------------------------------
    # 5. Check duplicate country-quarter observations
    # --------------------------------------------------

    duplicates = df.duplicated(
        [
            "geo",
            "year",
            "quarter",
        ]
    ).sum()

    print(
        f"\nDuplicate country-quarter rows: "
        f"{duplicates}"
    )

    if duplicates > 0:
        raise ValueError(
            f"Found {duplicates} duplicate "
            f"population observations."
        )

    # --------------------------------------------------
    # 6. Create standard period field
    # --------------------------------------------------

    df["period"] = (
        df["year"].astype(str)
        + "-Q"
        + df["quarter"].astype(str)
    )

    # --------------------------------------------------
    # 7. Select final columns
    # --------------------------------------------------

    df = df.rename(
        columns={
            "geo": "country_code"
        }
    )

    df = df[
        [
            "country_code",
            "country",
            "period",
            "year",
            "quarter",
            "population",
        ]
    ]

    df = df.sort_values(
        [
            "country_code",
            "year",
            "quarter",
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # 8. Basic validation
    # --------------------------------------------------

    if df["population"].isna().any():
        raise ValueError(
            "Missing population values detected."
        )

    if not (
        df["population"] > 0
    ).all():
        raise ValueError(
            "Invalid population values detected."
        )

    # --------------------------------------------------
    # 9. Coverage report
    # --------------------------------------------------

    print("\nPopulation coverage:")

    print(
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

    print("\nSample:")
    print(
        df.head(30).to_string(
            index=False
        )
    )

    # --------------------------------------------------
    # 10. Save
    # --------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()