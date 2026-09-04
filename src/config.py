from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

AIR_QUALITY_PROVIDER = os.getenv(
    "AIR_QUALITY_PROVIDER",
    "open_meteo",
)

FEAST_PROJECT = os.getenv(
    "FEAST_PROJECT",
    "pearls_aqi",
)

FEAST_REPO_PATH = os.getenv(
    "FEAST_REPO_PATH",
    "feature_repo",
)

MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "sqlite:///mlflow.db",
)

MLFLOW_EXPERIMENT_NAME = os.getenv(
    "MLFLOW_EXPERIMENT_NAME",
    "pearls_aqi_prediction",
)

MLFLOW_MODEL_NAME = os.getenv(
    "MLFLOW_MODEL_NAME",
    "pearls_aqi_model",
)

MLFLOW_MODEL_ALIAS = os.getenv(
    "MLFLOW_MODEL_ALIAS",
    "champion",
)

BACKFILL_DAYS = int(
    os.getenv("BACKFILL_DAYS", "180")
)


CITIES = {
    "Gujrat": {
        "latitude": 32.5736,
        "longitude": 74.0780,
        "country": "PK",
    },
    "Lahore": {
        "latitude": 31.5204,
        "longitude": 74.3587,
        "country": "PK",
    },
    "Islamabad": {
        "latitude": 33.6844,
        "longitude": 73.0479,
        "country": "PK",
    },
    "Karachi": {
        "latitude": 24.8607,
        "longitude": 67.0011,
        "country": "PK",
    },
    "Rawalpindi": {
        "latitude": 33.5651,
        "longitude": 73.0169,
        "country": "PK",
    },
}


# Backward-compatible default city.
CITY_NAME = os.getenv("CITY_NAME", "Gujrat")

if CITY_NAME not in CITIES:
    raise ValueError(
        f"Unknown CITY_NAME={CITY_NAME}. "
        f"Available cities: {list(CITIES)}"
    )

LATITUDE = CITIES[CITY_NAME]["latitude"]
LONGITUDE = CITIES[CITY_NAME]["longitude"]
COUNTRY_CODE = CITIES[CITY_NAME]["country"]
FEATURE_DIR = Path('data/features')


