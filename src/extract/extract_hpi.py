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


DATASET = "prc_hpi_q"


def main():

    print("Downloading Eurostat House Price Index...")

    data = fetch_eurostat(DATASET)

    df = jsonstat_to_dataframe(data)

    print("Raw shape:", df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nUnique units:")
    print(df["unit"].unique())

    print("\nUnique purchase categories:")
    print(df["purchase"].unique())

    # Keep only our countries

    df = df[
        df["geo"].isin(COUNTRIES.keys())
    ].copy()

    # Keep observations from 2015 onward

    df["year"] = (
        df["time"]
        .str[:4]
        .astype(int)
    )

    df = df[
        df["year"] >= 2015
    ].copy()

    output = (
        EUROSTAT_RAW_DIR /
        "house_price_index_raw.csv"
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
    print(df.head(20))


if __name__ == "__main__":
    main()
    