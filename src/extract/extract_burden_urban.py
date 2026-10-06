import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    COUNTRIES,
    EUROSTAT_RAW_DIR,
)

from src.extract.eurostat_api import (
    fetch_eurostat,
    jsonstat_to_dataframe,
)


DATASET = "ilc_lvho07d"


def main():

    frames = []

    for code, country in COUNTRIES.items():

        print(
            f"Downloading burden data: {country}"
        )

        data = fetch_eurostat(
            DATASET,
            {
                "geo": code,
                "sinceTimePeriod": "2015",
            },
        )

        temp = jsonstat_to_dataframe(data)

        frames.append(temp)

    df = pd.concat(
        frames,
        ignore_index=True,
    )

    print("\nColumns:")
    print(df.columns.tolist())

    for column in df.columns:

        if column not in [
            "time",
            "value",
            "geo",
        ]:

            print(f"\n{column}:")

            print(
                df[column]
                .value_counts()
                .head(30)
            )

    output = (
        EUROSTAT_RAW_DIR /
        "housing_burden_urban_raw.csv"
    )

    df.to_csv(
        output,
        index=False,
    )

    print("\nSaved:")
    print(output)


if __name__ == "__main__":
    main()