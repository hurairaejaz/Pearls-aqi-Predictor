from __future__ import annotations

from pathlib import Path

import pandas as pd
from feast import FeatureStore

from src.config import FEATURE_DIR, FEAST_REPO_PATH


FEATURE_FILE = FEATURE_DIR / "aqi_features.parquet"


def save_feature_dataframe(df: pd.DataFrame) -> Path:
    FEATURE_DIR.mkdir(parents=True, exist_ok=True)

    if FEATURE_FILE.exists():
        old = pd.read_parquet(FEATURE_FILE)
        df = pd.concat([old, df], ignore_index=True)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    df = (
        df.drop_duplicates(["city", "timestamp"])
        .sort_values(["city", "timestamp"])
        .reset_index(drop=True)
    )

    df.to_parquet(FEATURE_FILE, index=False)

    return FEATURE_FILE


def get_feast_store() -> FeatureStore:
    return FeatureStore(repo_path=FEAST_REPO_PATH)


def materialize_to_online_store(
    end_timestamp: pd.Timestamp | None = None,
) -> None:
    store = get_feast_store()

    if end_timestamp is None:
        end_timestamp = pd.Timestamp.now(tz="UTC")

    start_timestamp = end_timestamp - pd.Timedelta(days=30)

    store.materialize(
        start_date=start_timestamp.to_pydatetime(),
        end_date=end_timestamp.to_pydatetime(),
    )


def get_latest_online_features(city: str) -> dict:
    store = get_feast_store()

    feature_names = [
        "aqi",
        "co",
        "no2",
        "o3",
        "so2",
        "pm2_5",
        "pm10",
        "temperature",
        "humidity",
        "pressure",
        "wind_speed",
        "wind_direction",
        "clouds",
        "hour",
        "day",
        "day_of_week",
        "month",
        "week",
        "is_weekend",
        "hour_sin",
        "hour_cos",
        "month_sin",
        "month_cos",
        "aqi_lag_1h",
        "aqi_lag_3h",
        "aqi_lag_6h",
        "aqi_lag_12h",
        "aqi_lag_24h",
        "pm25_lag_1h",
        "pm25_lag_3h",
        "pm25_lag_6h",
        "pm25_lag_12h",
        "pm25_lag_24h",
        "aqi_rolling_3h",
        "aqi_rolling_6h",
        "aqi_rolling_12h",
        "aqi_rolling_24h",
        "pm25_rolling_6h",
        "pm25_rolling_24h",
        "aqi_change",
        "aqi_percentage_change",
        "pm25_change",
        "temperature_change",
        "humidity_change",
    ]

    response = store.get_online_features(
        features=[
            f"aqi_features:{name}"
            for name in feature_names
        ],
        entity_rows=[
            {"city": city}
        ],
    ).to_dict()

    return {
        key: (
            values[0]
            if isinstance(values, list) and values
            else None
        )
        for key, values in response.items()
    }