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
    "housing_burden_income_raw.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "housing_burden_income.csv"
)


QUINTILE_NAMES = {
    "TOTAL": "Total",
    "QU1": "Lowest 20%",
    "QU2": "Second 20%",
    "QU3": "Middle 20%",
    "QU4": "Fourth 20%",
    "QU5": "Highest 20%",
}


QUINTILE_ORDER = {
    "TOTAL": 0,
    "QU1": 1,
    "QU2": 2,
    "QU3": 3,
    "QU4": 4,
    "QU5": 5,
}


def main():

    print(
        "Transforming housing-cost "
        "burden by income quintile..."
    )

    # --------------------------------------------------
    # 1. Load raw Eurostat data
    # --------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    print(f"Raw rows: {len(df):,}")

    # --------------------------------------------------
    # 2. Filter to expected Eurostat dimensions
    # --------------------------------------------------

    df = df[
        (df["freq"] == "A")
        &
        (df["unit"] == "PC")
        &
        (df["geo"].isin(COUNTRIES.keys()))
        &
        (df["quant_inc"].isin(QUINTILE_NAMES.keys()))
    ].copy()

    print(
        f"Rows after filtering: "
        f"{len(df):,}"
    )

    # --------------------------------------------------
    # 3. Rename analytical columns
    # --------------------------------------------------

    df = df.rename(
        columns={
            "geo": "country_code",
            "time": "year",
            "quant_inc": "income_group_code",
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
    # 5. Add readable income groups
    # --------------------------------------------------

    df["income_group"] = (
        df["income_group_code"]
        .map(QUINTILE_NAMES)
    )

    df["income_group_order"] = (
        df["income_group_code"]
        .map(QUINTILE_ORDER)
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
            "income_group_order",
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # 9. Final columns
    # --------------------------------------------------

    df = df[
        [
            "country_code",
            "country",
            "year",
            "income_group_code",
            "income_group",
            "income_group_order",
            "housing_overburden_rate",
        ]
    ]

    # --------------------------------------------------
    # 10. Basic diagnostic
    # --------------------------------------------------

    print("\nRows by income group:")

    print(
        df["income_group_code"]
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