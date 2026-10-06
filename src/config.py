from pathlib import Path


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FINAL_DIR = DATA_DIR / "final"

EUROSTAT_RAW_DIR = RAW_DIR / "eurostat"
ECB_RAW_DIR = RAW_DIR / "ecb"


# --------------------------------------------------
# COUNTRIES
# --------------------------------------------------

COUNTRIES = {
    "DE": "Germany",
    "FR": "France",
    "NL": "Netherlands",
    "BE": "Belgium",
    "IE": "Ireland",
    "ES": "Spain",
    "PT": "Portugal",
}


# --------------------------------------------------
# ANALYTICAL PERIOD
# --------------------------------------------------

START_YEAR = 2015
END_YEAR = 2026

BASE_YEAR = 2015


# --------------------------------------------------
# EUROSTAT
# --------------------------------------------------

EUROSTAT_BASE_URL = (
    "https://ec.europa.eu/eurostat/api/"
    "dissemination/statistics/1.0/data"
)