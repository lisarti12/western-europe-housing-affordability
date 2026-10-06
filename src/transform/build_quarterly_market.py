import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    COUNTRIES,
    PROCESSED_DIR,
    FINAL_DIR,
)


HPI_FILE = (
    PROCESSED_DIR /
    "house_price_index.csv"
)

RENT_FILE = (
    PROCESSED_DIR /
    "rent_index_quarterly.csv"
)

MORTGAGE_FILE = (
    PROCESSED_DIR /
    "mortgage_rates_quarterly.csv"
)

OUTPUT_FILE = (
    FINAL_DIR /
    "fact_market_quarterly.csv"
)


def main():

    print("Building final quarterly market dataset...")

    # --------------------------------------------------
    # 1. Load datasets
    # --------------------------------------------------

    hpi = pd.read_csv(HPI_FILE)
    rent = pd.read_csv(RENT_FILE)
    mortgage = pd.read_csv(MORTGAGE_FILE)

    print(f"HPI rows: {len(hpi):,}")
    print(f"Rent rows: {len(rent):,}")
    print(f"Mortgage rows: {len(mortgage):,}")

    # --------------------------------------------------
    # 2. Keep required columns
    # --------------------------------------------------

    keys = [
        "country_code",
        "country",
        "period",
        "year",
        "quarter",
    ]

    hpi = hpi[
        keys
        + [
            "hpi_2015_100",
        ]
    ].copy()

    rent = rent[
        keys
        + [
            "rent_2015_100",
        ]
    ].copy()

    mortgage = mortgage[
        keys
        + [
            "mortgage_rate",
        ]
    ].copy()

    # --------------------------------------------------
    # 3. Validate source uniqueness
    # --------------------------------------------------

    for name, frame in [
        ("HPI", hpi),
        ("Rent", rent),
        ("Mortgage", mortgage),
    ]:

        duplicates = frame.duplicated(
            [
                "country_code",
                "period",
            ]
        ).sum()

        if duplicates > 0:
            raise ValueError(
                f"{name} contains "
                f"{duplicates} duplicate "
                f"country-quarter rows."
            )

    # --------------------------------------------------
    # 4. Use HPI as the core quarterly timeline
    # --------------------------------------------------
    #
    # HPI is our core housing-market measure.
    # Therefore we preserve every HPI observation
    # and attach rent/mortgage data where available.
    #
    # This also prevents mortgage observations from
    # Q3 2026 creating rows where no HPI exists yet.
    # --------------------------------------------------

    market = hpi.merge(
        rent,
        on=keys,
        how="left",
        validate="one_to_one",
    )

    market = market.merge(
        mortgage,
        on=keys,
        how="left",
        validate="one_to_one",
    )

    # --------------------------------------------------
    # 5. Sort
    # --------------------------------------------------

    market = market.sort_values(
        [
            "country_code",
            "year",
            "quarter",
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # 6. Check country coverage
    # --------------------------------------------------

    expected = set(COUNTRIES.keys())

    actual = set(
        market["country_code"].unique()
    )

    if actual != expected:
        raise ValueError(
            f"Country mismatch. "
            f"Expected {expected}, "
            f"found {actual}"
        )

    # --------------------------------------------------
    # 7. Missing-value report
    # --------------------------------------------------

    print("\nMissing values:")

    missing = (
        market[
            [
                "hpi_2015_100",
                "rent_2015_100",
                "mortgage_rate",
            ]
        ]
        .isna()
        .sum()
    )

    print(missing)

    # HPI must never be missing because it defines
    # the core timeline.

    if market["hpi_2015_100"].isna().any():
        raise ValueError(
            "Missing HPI values detected."
        )

    # --------------------------------------------------
    # 8. Explain missing mortgage observations
    # --------------------------------------------------

    mortgage_missing = market[
        market["mortgage_rate"].isna()
    ]

    print("\nMortgage-rate missingness by country:")

    print(
        mortgage_missing[
            "country"
        ]
        .value_counts()
        .sort_index()
    )

    # --------------------------------------------------
    # 9. Create completeness flags
    # --------------------------------------------------

    market["has_rent_data"] = (
        market["rent_2015_100"]
        .notna()
    )

    market["has_mortgage_data"] = (
        market["mortgage_rate"]
        .notna()
    )

    market["has_complete_market_data"] = (
        market["has_rent_data"]
        &
        market["has_mortgage_data"]
    )

    # --------------------------------------------------
    # 10. Calculate quarterly HPI change
    # --------------------------------------------------

    market["hpi_qoq_pct"] = (
        market.groupby("country_code")
        ["hpi_2015_100"]
        .pct_change(fill_method=None)
        * 100
    )

    # --------------------------------------------------
    # 11. Calculate quarterly rent change
    # --------------------------------------------------

    market["rent_qoq_pct"] = (
        market.groupby("country_code")
        ["rent_2015_100"]
        .pct_change(fill_method=None)
        * 100
    )

    # --------------------------------------------------
    # 12. Calculate year-over-year quarterly HPI
    # --------------------------------------------------

    market["hpi_yoy_pct"] = (
        market.groupby("country_code")
        ["hpi_2015_100"]
        .pct_change(
            periods=4,
            fill_method=None,
        )
        * 100
    )

    # --------------------------------------------------
    # 13. Calculate year-over-year quarterly rent
    # --------------------------------------------------

    market["rent_yoy_pct"] = (
        market.groupby("country_code")
        ["rent_2015_100"]
        .pct_change(
            periods=4,
            fill_method=None,
        )
        * 100
    )

    # --------------------------------------------------
    # 14. Round analytical fields
    # --------------------------------------------------

    round_columns = [
        "hpi_2015_100",
        "rent_2015_100",
        "mortgage_rate",
        "hpi_qoq_pct",
        "rent_qoq_pct",
        "hpi_yoy_pct",
        "rent_yoy_pct",
    ]

    market[round_columns] = (
        market[round_columns]
        .round(2)
    )

    # --------------------------------------------------
    # 15. Final column order
    # --------------------------------------------------

    market = market[
        [
            "country_code",
            "country",
            "period",
            "year",
            "quarter",

            "hpi_2015_100",
            "rent_2015_100",
            "mortgage_rate",

            "hpi_qoq_pct",
            "rent_qoq_pct",
            "hpi_yoy_pct",
            "rent_yoy_pct",

            "has_rent_data",
            "has_mortgage_data",
            "has_complete_market_data",
        ]
    ]

    # --------------------------------------------------
    # 16. Coverage
    # --------------------------------------------------

    print("\nFinal quarterly coverage:")

    print(
        market.groupby("country")
        .agg(
            first_period=("period", "min"),
            last_period=("period", "max"),
            observations=("period", "count"),
            mortgage_observations=(
                "has_mortgage_data",
                "sum",
            ),
        )
    )

    # --------------------------------------------------
    # 17. Latest observations
    # --------------------------------------------------

    latest = (
        market
        .sort_values(
            [
                "country_code",
                "year",
                "quarter",
            ]
        )
        .groupby("country_code")
        .tail(1)
    )

    print("\nLatest quarterly observations:")

    print(
        latest[
            [
                "country",
                "period",
                "hpi_2015_100",
                "rent_2015_100",
                "mortgage_rate",
            ]
        ]
        .sort_values("country")
        .to_string(index=False)
    )

    # --------------------------------------------------
    # 18. Save
    # --------------------------------------------------

    FINAL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    market.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"\nFinal rows: {len(market):,}")

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()