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


DATASET = "namq_10_pe"


def main():

    print(
        "Downloading Eurostat national-accounts "
        "population data..."
    )

    frames = []

    for code, country in COUNTRIES.items():

        print(
            f"Downloading population: {country}"
        )

        data = fetch_eurostat(
            DATASET,
            {
                "geo": code,
                "sinceTimePeriod": "2015-Q1",
            }
        )

        temp = jsonstat_to_dataframe(data)

        frames.append(temp)

    if not frames:
        raise ValueError(
            "No population data downloaded."
        )

    df = pd.concat(
        frames,
        ignore_index=True
    )

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nAvailable dimension values:")

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
                .head(50)
            )

    output = (
        EUROSTAT_RAW_DIR /
        "population_raw.csv"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output,
        index=False
    )

    print("\nSaved:")
    print(output)

    print("\nSample:")
    print(
        df.head(30).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()