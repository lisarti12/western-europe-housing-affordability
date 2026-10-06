import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# ------------------------------------------------------------
# Project setup
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.config import FINAL_DIR, PROCESSED_DIR


# ------------------------------------------------------------
# File locations
# ------------------------------------------------------------

ANNUAL_FILE = (
    FINAL_DIR /
    "fact_affordability_annual.csv"
)

QUARTERLY_FILE = (
    FINAL_DIR /
    "fact_market_quarterly.csv"
)

BURDEN_INCOME_FILE = (
    PROCESSED_DIR /
    "housing_burden_income.csv"
)

BURDEN_URBAN_FILE = (
    PROCESSED_DIR /
    "housing_burden_urban.csv"
)


# ------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def main():

    print("Loading analytical data into PostgreSQL...\n")

    # --------------------------------------------------------
    # 1. Read CSV files
    # --------------------------------------------------------

    annual = pd.read_csv(ANNUAL_FILE)
    quarterly = pd.read_csv(QUARTERLY_FILE)
    burden_income = pd.read_csv(BURDEN_INCOME_FILE)
    burden_urban = pd.read_csv(BURDEN_URBAN_FILE)

    print(f"Annual CSV rows: {len(annual):,}")
    print(f"Quarterly CSV rows: {len(quarterly):,}")
    print(
        f"Burden income CSV rows: "
        f"{len(burden_income):,}"
    )
    print(
        f"Burden urban CSV rows: "
        f"{len(burden_urban):,}"
    )

    # --------------------------------------------------------
    # 2. Remove country name
    #
    # PostgreSQL stores country names in dim_country.
    # Fact tables only need country_code.
    # --------------------------------------------------------

    annual = annual.drop(
        columns=["country"]
    )

    quarterly = quarterly.drop(
        columns=["country"]
    )

    burden_income = burden_income.drop(
        columns=["country"]
    )

    burden_urban = burden_urban.drop(
        columns=["country"]
    )

    # --------------------------------------------------------
    # 3. Build database connection
    # --------------------------------------------------------

    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
    )

    engine = create_engine(
        connection_url
    )

    # --------------------------------------------------------
    # 4. Test connection
    # --------------------------------------------------------

    with engine.connect() as connection:

        database = connection.execute(
            text(
                "SELECT current_database();"
            )
        ).scalar_one()

        print(
            f"\nConnected to {database}"
        )

    # --------------------------------------------------------
    # 5. Load all four fact tables
    #
    # Everything happens inside one transaction.
    # If one load fails, PostgreSQL rolls the transaction back.
    # --------------------------------------------------------

    with engine.begin() as connection:

        print(
            "\nClearing existing fact tables..."
        )

        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    fact_affordability_annual,
                    fact_market_quarterly,
                    fact_burden_income,
                    fact_burden_urban;
                """
            )
        )

        print(
            "Loading fact_affordability_annual..."
        )

        annual.to_sql(
            "fact_affordability_annual",
            con=connection,
            if_exists="append",
            index=False,
            method="multi",
        )

        print(
            "Loading fact_market_quarterly..."
        )

        quarterly.to_sql(
            "fact_market_quarterly",
            con=connection,
            if_exists="append",
            index=False,
            method="multi",
        )

        print(
            "Loading fact_burden_income..."
        )

        burden_income.to_sql(
            "fact_burden_income",
            con=connection,
            if_exists="append",
            index=False,
            method="multi",
        )

        print(
            "Loading fact_burden_urban..."
        )

        burden_urban.to_sql(
            "fact_burden_urban",
            con=connection,
            if_exists="append",
            index=False,
            method="multi",
        )

    # --------------------------------------------------------
    # 6. Validate PostgreSQL row counts
    # --------------------------------------------------------

    with engine.connect() as connection:

        annual_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM fact_affordability_annual;
                """
            )
        ).scalar_one()

        quarterly_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM fact_market_quarterly;
                """
            )
        ).scalar_one()

        burden_income_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM fact_burden_income;
                """
            )
        ).scalar_one()

        burden_urban_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM fact_burden_urban;
                """
            )
        ).scalar_one()

    print("\nPostgreSQL row counts:")

    print(
        "fact_affordability_annual:",
        annual_count,
    )

    print(
        "fact_market_quarterly:",
        quarterly_count,
    )

    print(
        "fact_burden_income:",
        burden_income_count,
    )

    print(
        "fact_burden_urban:",
        burden_urban_count,
    )

    # --------------------------------------------------------
    # 7. Compare PostgreSQL counts against source CSVs
    # --------------------------------------------------------

    expected_counts = {
        "fact_affordability_annual": len(annual),
        "fact_market_quarterly": len(quarterly),
        "fact_burden_income": len(burden_income),
        "fact_burden_urban": len(burden_urban),
    }

    actual_counts = {
        "fact_affordability_annual": annual_count,
        "fact_market_quarterly": quarterly_count,
        "fact_burden_income": burden_income_count,
        "fact_burden_urban": burden_urban_count,
    }

    for table_name in expected_counts:

        expected = expected_counts[
            table_name
        ]

        actual = actual_counts[
            table_name
        ]

        if actual != expected:

            raise ValueError(
                f"{table_name}: expected "
                f"{expected} rows but PostgreSQL "
                f"contains {actual}."
            )

    # --------------------------------------------------------
    # 8. Final result
    # --------------------------------------------------------

    print(
        "\nPOSTGRESQL LOAD PASSED"
    )


if __name__ == "__main__":
    main()