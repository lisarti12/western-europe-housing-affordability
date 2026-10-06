import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    COUNTRIES,
    PROCESSED_DIR,
)


HPI_FILE = (
    PROCESSED_DIR /
    "house_price_index.csv"
)

RENT_FILE = (
    PROCESSED_DIR /
    "rent_index_quarterly.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "market_annual.csv"
)


def main():

    print("Building annual housing market dataset...")

    # --------------------------------------------------
    # 1. Load processed quarterly datasets
    # --------------------------------------------------

    hpi = pd.read_csv(HPI_FILE)
    rent = pd.read_csv(RENT_FILE)

    print(
        f"HPI quarterly rows: {len(hpi):,}"
    )

    print(
        f"Rent quarterly rows: {len(rent):,}"
    )

    # --------------------------------------------------
    # 2. Convert HPI to annual averages
    # --------------------------------------------------

    annual_hpi = (
        hpi.groupby(
            [
                "country_code",
                "country",
                "year",
            ],
            as_index=False,
        )
        .agg(
            hpi_2015_100=(
                "hpi_2015_100",
                "mean",
            ),
            hpi_quarters_available=(
                "quarter",
                "count",
            ),
        )
    )

    annual_hpi["hpi_2015_100"] = (
        annual_hpi["hpi_2015_100"]
        .round(2)
    )

    # --------------------------------------------------
    # 3. Convert rent to annual averages
    # --------------------------------------------------

    annual_rent = (
        rent.groupby(
            [
                "country_code",
                "country",
                "year",
            ],
            as_index=False,
        )
        .agg(
            rent_2015_100=(
                "rent_2015_100",
                "mean",
            ),
            rent_quarters_available=(
                "quarter",
                "count",
            ),
        )
    )

    annual_rent["rent_2015_100"] = (
        annual_rent["rent_2015_100"]
        .round(2)
    )

    # --------------------------------------------------
    # 4. Merge house prices and rents
    # --------------------------------------------------

    annual = annual_hpi.merge(
        annual_rent,
        on=[
            "country_code",
            "country",
            "year",
        ],
        how="outer",
        validate="one_to_one",
    )

    # --------------------------------------------------
    # 5. Check missing market data
    # --------------------------------------------------

    print("\nMissing values after merge:")

    print(
        annual[
            [
                "hpi_2015_100",
                "rent_2015_100",
            ]
        ]
        .isna()
        .sum()
    )

    # --------------------------------------------------
    # 6. Identify complete years
    # --------------------------------------------------

    annual["market_is_full_year"] = (
        (annual["hpi_quarters_available"] == 4)
        &
        (annual["rent_quarters_available"] == 4)
    )

    # --------------------------------------------------
    # 7. Sort
    # --------------------------------------------------

    annual = annual.sort_values(
        [
            "country_code",
            "year",
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------
    # 8. Validate 2015 baselines
    # --------------------------------------------------

    baseline = annual[
        annual["year"] == 2015
    ]

    print("\n2015 market baselines:")

    print(
        baseline[
            [
                "country",
                "hpi_2015_100",
                "rent_2015_100",
            ]
        ].to_string(index=False)
    )

    hpi_error = (
        baseline["hpi_2015_100"]
        - 100
    ).abs().max()

    rent_error = (
        baseline["rent_2015_100"]
        - 100
    ).abs().max()

    if hpi_error >= 0.1:
        raise ValueError(
            "HPI 2015 baseline validation failed."
        )

    if rent_error >= 0.1:
        raise ValueError(
            "Rent 2015 baseline validation failed."
        )

    # --------------------------------------------------
    # 9. Historical completeness check
    # --------------------------------------------------

    historical = annual[
        annual["year"] <= 2025
    ]

    incomplete_historical = historical[
        ~historical[
            "market_is_full_year"
        ]
    ]

    print(
        "\nIncomplete market observations "
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
                    "hpi_quarters_available",
                    "rent_quarters_available",
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------
    # 10. Report partial 2026 observations
    # --------------------------------------------------

    partial = annual[
        ~annual["market_is_full_year"]
    ]

    print("\nPartial-year market observations:")

    if partial.empty:

        print("None")

    else:

        print(
            partial[
                [
                    "country",
                    "year",
                    "hpi_quarters_available",
                    "rent_quarters_available",
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------
    # 11. Save
    # --------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    annual.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nAnnual market sample:")

    print(
        annual.head(30)
        .to_string(index=False)
    )

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()