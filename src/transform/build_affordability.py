import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    PROCESSED_DIR,
    FINAL_DIR,
)


MARKET_FILE = (
    PROCESSED_DIR /
    "market_annual.csv"
)

INCOME_FILE = (
    PROCESSED_DIR /
    "income_annual.csv"
)

OUTPUT_FILE = (
    FINAL_DIR /
    "fact_affordability_annual.csv"
)


def main():

    print("Building final affordability dataset...")

    # --------------------------------------------------
    # 1. Load annual market and income data
    # --------------------------------------------------

    market = pd.read_csv(MARKET_FILE)
    income = pd.read_csv(INCOME_FILE)

    print(
        f"Market rows: {len(market):,}"
    )

    print(
        f"Income rows: {len(income):,}"
    )

    # --------------------------------------------------
    # 2. Merge market + income
    # --------------------------------------------------

    df = market.merge(
        income[
            [
                "country_code",
                "country",
                "year",
                "income_per_capita_eur",
                "income_2015_100",
                "quarters_available",
                "is_full_year",
            ]
        ],
        on=[
            "country_code",
            "country",
            "year",
        ],
        how="inner",
        validate="one_to_one",
    )

    print(
        f"Rows after merge: {len(df):,}"
    )

    # --------------------------------------------------
    # 3. Check for missing values
    # --------------------------------------------------

    important_columns = [
        "hpi_2015_100",
        "rent_2015_100",
        "income_per_capita_eur",
        "income_2015_100",
    ]

    missing = (
        df[important_columns]
        .isna()
        .sum()
    )

    print("\nMissing analytical values:")
    print(missing)

    if missing.sum() > 0:
        raise ValueError(
            "Missing analytical values "
            "after affordability merge."
        )

    # --------------------------------------------------
    # 4. Identify complete annual observations
    # --------------------------------------------------

    df["is_complete_year"] = (
        df["market_is_full_year"]
        &
        df["is_full_year"]
    )

    # --------------------------------------------------
    # 5. Growth since 2015
    # --------------------------------------------------
    #
    # Since every index is rebased to 2015 = 100:
    #
    # Index 150 = +50% since 2015
    # Index 125 = +25% since 2015
    # --------------------------------------------------

    df["hpi_growth_since_2015_pct"] = (
        df["hpi_2015_100"] - 100
    )

    df["rent_growth_since_2015_pct"] = (
        df["rent_2015_100"] - 100
    )

    df["income_growth_since_2015_pct"] = (
        df["income_2015_100"] - 100
    )

    # --------------------------------------------------
    # 6. Main affordability gaps
    # --------------------------------------------------
    #
    # Positive HPI-income gap:
    # house prices have grown faster than
    # disposable income per capita.
    #
    # Positive rent-income gap:
    # rents have grown faster than
    # disposable income per capita.
    #
    # Unit = percentage points.
    # --------------------------------------------------

    df["hpi_income_gap_pp"] = (
        df["hpi_growth_since_2015_pct"]
        -
        df["income_growth_since_2015_pct"]
    )

    df["rent_income_gap_pp"] = (
        df["rent_growth_since_2015_pct"]
        -
        df["income_growth_since_2015_pct"]
    )

    # --------------------------------------------------
    # 7. Sort BEFORE calculating YoY
    # --------------------------------------------------

    df = df.sort_values(
        [
            "country_code",
            "year",
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # 8. Year-over-year growth
    # --------------------------------------------------

    df["hpi_yoy_pct"] = (
        df.groupby("country_code")
        ["hpi_2015_100"]
        .pct_change(fill_method=None)
        * 100
    )

    df["rent_yoy_pct"] = (
        df.groupby("country_code")
        ["rent_2015_100"]
        .pct_change(fill_method=None)
        * 100
    )

    df["income_yoy_pct"] = (
        df.groupby("country_code")
        ["income_2015_100"]
        .pct_change(fill_method=None)
        * 100
    )

    # --------------------------------------------------
    # 9. Round analytical metrics
    # --------------------------------------------------

    round_columns = [
        "income_per_capita_eur",
        "hpi_2015_100",
        "rent_2015_100",
        "income_2015_100",
        "hpi_growth_since_2015_pct",
        "rent_growth_since_2015_pct",
        "income_growth_since_2015_pct",
        "hpi_income_gap_pp",
        "rent_income_gap_pp",
        "hpi_yoy_pct",
        "rent_yoy_pct",
        "income_yoy_pct",
    ]

    df[round_columns] = (
        df[round_columns]
        .round(2)
    )

    # --------------------------------------------------
    # 10. Final analytical columns
    # --------------------------------------------------

    df = df[
        [
            "country_code",
            "country",
            "year",

            "hpi_2015_100",
            "rent_2015_100",
            "income_per_capita_eur",
            "income_2015_100",

            "hpi_growth_since_2015_pct",
            "rent_growth_since_2015_pct",
            "income_growth_since_2015_pct",

            "hpi_income_gap_pp",
            "rent_income_gap_pp",

            "hpi_yoy_pct",
            "rent_yoy_pct",
            "income_yoy_pct",

            "is_complete_year",
        ]
    ]

    # --------------------------------------------------
    # 11. Validate historical completeness
    # --------------------------------------------------

    historical = df[
        df["year"] <= 2025
    ]

    incomplete_historical = historical[
        ~historical["is_complete_year"]
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
                ]
            ].to_string(index=False)
        )

        raise ValueError(
            "Incomplete observations "
            "exist before 2026."
        )

    # --------------------------------------------------
    # 12. Check 2015 gaps
    # --------------------------------------------------

    baseline = df[
        df["year"] == 2015
    ]

    max_hpi_gap = (
        baseline["hpi_income_gap_pp"]
        .abs()
        .max()
    )

    max_rent_gap = (
        baseline["rent_income_gap_pp"]
        .abs()
        .max()
    )

    if max_hpi_gap >= 0.1:
        raise ValueError(
            "2015 HPI-income gap "
            "should be zero."
        )

    if max_rent_gap >= 0.1:
        raise ValueError(
            "2015 rent-income gap "
            "should be zero."
        )

    # --------------------------------------------------
    # 13. Show latest complete year
    # --------------------------------------------------

    latest_complete_year = (
        df[
            df["is_complete_year"]
        ]["year"]
        .max()
    )

    print(
        f"\nLatest complete year: "
        f"{latest_complete_year}"
    )

    latest = df[
        df["year"] == latest_complete_year
    ].copy()

    print(
        "\nLatest affordability results:"
    )

    print(
        latest[
            [
                "country",
                "hpi_growth_since_2015_pct",
                "rent_growth_since_2015_pct",
                "income_growth_since_2015_pct",
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

    # --------------------------------------------------
    # 14. Report partial observations
    # --------------------------------------------------

    partial = df[
        ~df["is_complete_year"]
    ]

    print(
        "\nPartial-year observations "
        "excluded from full-year comparisons:"
    )

    if partial.empty:
        print("None")

    else:
        print(
            partial[
                [
                    "country",
                    "year",
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------
    # 15. Save final dataset
    # --------------------------------------------------

    FINAL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nFinal rows:")
    print(len(df))

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()