import sys
from pathlib import Path
from io import StringIO

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    COUNTRIES,
    ECB_RAW_DIR,
)


BASE_URL = (
    "https://data-api.ecb.europa.eu/"
    "service/data/MIR"
)


def download_country(country_code):

    key = (
        f"M.{country_code}.B."
        f"A2C.A.R.A.2250.EUR.N"
    )

    url = f"{BASE_URL}/{key}"

    params = {
        "startPeriod": "2015-01",
    }

    headers = {
        "Accept": "text/csv"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=120,
    )

    response.raise_for_status()

    return pd.read_csv(
        StringIO(response.text)
    )


def main():

    frames = []

    for code, country in COUNTRIES.items():

        print(
            f"Downloading mortgage rate: {country}"
        )

        try:

            temp = download_country(code)

            temp["country_code"] = code
            temp["country"] = country

            frames.append(temp)

        except Exception as error:

            print(
                f"WARNING: {country}: {error}"
            )

    if not frames:
        raise ValueError(
            "ECB returned no mortgage data."
        )

    df = pd.concat(
        frames,
        ignore_index=True,
    )

    ECB_RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = (
        ECB_RAW_DIR /
        "mortgage_rates_raw.csv"
    )

    df.to_csv(
        output,
        index=False,
    )

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nSaved:")
    print(output)


if __name__ == "__main__":
    main()  