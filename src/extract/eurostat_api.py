import requests
import pandas as pd


BASE_URL = (
    "https://ec.europa.eu/eurostat/api/"
    "dissemination/statistics/1.0/data"
)


def fetch_eurostat(dataset_code, params=None):
    """
    Download a Eurostat dataset through the dissemination API.
    """

    url = f"{BASE_URL}/{dataset_code}"

    query_params = {"lang": "en"}

    if params:
        query_params.update(params)

    response = requests.get(
        url,
        params=query_params,
        timeout=120
    )

    response.raise_for_status()

    return response.json()


def _ordered_categories(dimension):
    """
    Return category codes in Eurostat's numerical order.
    """

    category = dimension["category"]

    index = category["index"]

    if isinstance(index, dict):
        return [
            key
            for key, value
            in sorted(index.items(), key=lambda x: x[1])
        ]

    return index


def jsonstat_to_dataframe(data):
    """
    Convert Eurostat JSON-stat response into a tidy pandas DataFrame.
    """

    dimensions = data["id"]
    sizes = data["size"]

    dimension_values = {}

    for dimension_name in dimensions:

        dimension = data["dimension"][dimension_name]

        dimension_values[dimension_name] = (
            _ordered_categories(dimension)
        )

    # Build every possible coordinate combination

    import itertools

    combinations = list(
        itertools.product(
            *[
                dimension_values[d]
                for d in dimensions
            ]
        )
    )

    values = data.get("value", {})

    records = []

    for flat_index, combination in enumerate(combinations):

        # Eurostat may encode values as dictionary or list

        if isinstance(values, dict):
            value = values.get(str(flat_index))
        else:
            value = (
                values[flat_index]
                if flat_index < len(values)
                else None
            )

        if value is None:
            continue

        record = dict(
            zip(dimensions, combination)
        )

        record["value"] = value

        records.append(record)

    return pd.DataFrame(records)