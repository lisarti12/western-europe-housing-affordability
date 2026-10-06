import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    ECB_RAW_DIR,
    PROCESSED_DIR,
)


INPUT_FILE = (
    ECB_RAW_DIR /
    "mortgage_rates_raw.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR /
    "mortgage_rates_quarterly.csv"
)


def main():

    df = pd.read_csv(INPUT_FILE)

    print("Columns:")
    print(df.columns.tolist())

    # ECB CSV currently exposes these SDMX observation
    # fields. We check rather than silently assume.

    required = [
        "TIME_PERIOD",
        "OBS_VALUE",
        "country_code",
        "country",
    ]

    missing_columns = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing ECB columns: "
            f"{missing_columns}"
        )

    df["date"] = pd.to_datetime(
        df["TIME_PERIOD"]
    )

    df["mortgage_rate"] = (
        pd.to_numeric(
            df["OBS_VALUE"],
            errors="coerce",
        )
    )

    df["year"] = (
        df["date"].dt.year
    )

    df["quarter"] = (
        df["date"].dt.quarter
    )

    quarterly = (
        df.groupby(
            [
                "country_code",
                "country",
                "year",
                "quarter",
            ],
            as_index=False,
        )
        ["mortgage_rate"]
        .mean()
    )

    quarterly["period"] = (
        quarterly["year"].astype(str)
        + "-Q"
        + quarterly["quarter"].astype(str)
    )

    quarterly["mortgage_rate"] = (
        quarterly["mortgage_rate"]
        .round(4)
    )

    quarterly = quarterly[
        [
            "country_code",
            "country",
            "period",
            "year",
            "quarter",
            "mortgage_rate",
        ]
    ]

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    quarterly.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nMortgage coverage:")

    print(
        quarterly.groupby("country")
        .agg(
            first_period=("period", "min"),
            last_period=("period", "max"),
            observations=("period", "count"),
        )
    )

    print("\nSaved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()