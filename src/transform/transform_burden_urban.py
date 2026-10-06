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
    "housing_burden_urban_raw.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "housing_burden_urban.csv"
)


URBAN_NAMES = {
    "TOTAL": "Total",
    "DEG1": "Cities",
    "DEG2": "Towns and suburbs",
    "DEG3": "Rural areas",
}


URBAN_ORDER = {
    "TOTAL": 0,
    "DEG1": 1,
    "DEG2": 2,
    "DEG3": 3,
}


def main():

    print(
        "Transforming housing-cost burden "
        "by degree of urbanisation..."
    )

    # --------------------------------------------------
    # 1. Load raw Eurostat data
    # --------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    print(f"Raw rows: {len(df):,}")

    # --------------------------------------------------
    # 2. Filter expected dimensions
    # --------------------------------------------------

    df = df[
        (df["freq"] == "A")
        &
        (df["unit"] == "PC")
        &
        (df["geo"].isin(COUNTRIES.keys()))
        &
        (df["deg_urb"].isin(["DEG1", "DEG2", "DEG3"]))
    ].copy()

    print(
        f"Rows after filtering: "
        f"{len(df):,}"
    )

    # --------------------------------------------------
    # 3. Rename columns
    # --------------------------------------------------

    df = df.rename(
        columns={
            "geo": "country_code",
            "time": "year",
            "deg_urb": "urbanisation_code",
            "value": "housing_overburden_rate",
        }
    )

    # --------------------------------------------------
    # 4. Add readable country names
    # --------------------------------------------------

    df["country"] = (
        df["country_code"]
        .map(COUNTRIES)
    )

    # --------------------------------------------------
    # 5. Add readable urbanisation categories
    # --------------------------------------------------

    df["urbanisation_group"] = (
        df["urbanisation_code"]
        .map(URBAN_NAMES)
    )

    df["urbanisation_order"] = (
        df["urbanisation_code"]
        .map(URBAN_ORDER)
    )

    # --------------------------------------------------
    # 6. Data types
    # --------------------------------------------------

    df["year"] = (
        pd.to_numeric(
            df["year"],
            errors="raise",
        )
        .astype(int)
    )

    df["housing_overburden_rate"] = (
        pd.to_numeric(
            df["housing_overburden_rate"],
            errors="coerce",
        )
    )

    # --------------------------------------------------
    # 7. Keep project period
    # --------------------------------------------------

    df = df[
        df["year"].between(
            2015,
            2025,
        )
    ].copy()

    # --------------------------------------------------
    # 8. Sort
    # --------------------------------------------------

    df = df.sort_values(
        [
            "country_code",
            "year",
            "urbanisation_order",
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # 9. Final analytical columns
    # --------------------------------------------------

    df = df[
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

    # --------------------------------------------------
    # 10. Diagnostics
    # --------------------------------------------------

    print("\nRows by urbanisation group:")

    print(
        df["urbanisation_code"]
        .value_counts()
        .sort_index()
    )

    print("\nCoverage by country:")

    print(
        df.groupby("country")
        .agg(
            first_year=("year", "min"),
            last_year=("year", "max"),
            observations=(
                "housing_overburden_rate",
                "count",
            ),
        )
    )

    # --------------------------------------------------
    # 11. Save
    # --------------------------------------------------

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()