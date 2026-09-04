from __future__ import annotations

import numpy as np
import pandas as pd


BASE_COLUMNS = [
    "timestamp",
    "city",
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
]


def _add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df["hour"] = df["timestamp"].dt.hour.astype("int64")
    df["day"] = df["timestamp"].dt.day.astype("int64")
    df["day_of_week"] = df["timestamp"].dt.dayofweek.astype("int64")
    df["month"] = df["timestamp"].dt.month.astype("int64")
    df["week"] = df["timestamp"].dt.isocalendar().week.astype("int64")
    df["is_weekend"] = (df["day_of_week"] >= 5).astype("int64")

    # Cyclic encodings prevent an artificial jump between 23 and 0.
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24).astype("float32")
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24).astype("float32")
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12).astype("float32")
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12).astype("float32")
    return df


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    for lag in (1, 3, 6, 12, 24):
        df[f"aqi_lag_{lag}h"] = df["aqi"].shift(lag)
        df[f"pm25_lag_{lag}h"] = df["pm2_5"].shift(lag)
    return df


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    for window in (3, 6, 12, 24):
        df[f"aqi_rolling_{window}h"] = (
            df["aqi"].rolling(window=window, min_periods=window).mean()
        )
    for window in (6, 24):
        df[f"pm25_rolling_{window}h"] = (
            df["pm2_5"].rolling(window=window, min_periods=window).mean()
        )
    return df


def add_change_features(df: pd.DataFrame) -> pd.DataFrame:
    df["aqi_change"] = df["aqi"].diff()
    previous = df["aqi"].shift(1)
    df["aqi_percentage_change"] = np.where(
        previous.abs() > 1e-9,
        (df["aqi"] - previous) / previous * 100.0,
        0.0,
    )
    df["pm25_change"] = df["pm2_5"].diff()
    df["temperature_change"] = df["temperature"].diff()
    df["humidity_change"] = df["humidity"].diff()
    return df


def add_targets(df: pd.DataFrame) -> pd.DataFrame:
    # Targets are true future values. With hourly observations, 24/48/72
    # rows correspond to 24/48/72 hours.
    df["target_24h"] = df["aqi"].shift(-24)
    df["target_48h"] = df["aqi"].shift(-48)
    df["target_72h"] = df["aqi"].shift(-72)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip()
    rename = {
        "us_aqi": "aqi",
        "carbon_monoxide": "co",
        "nitrogen_dioxide": "no2",
        "sulphur_dioxide": "so2",
        "ozone": "o3",
        "temperature_2m": "temperature",
        "relative_humidity_2m": "humidity",
        "pressure_msl": "pressure",
        "wind_speed_10m": "wind_speed",
        "wind_direction_10m": "wind_direction",
        "cloud_cover": "clouds",
    }
    df = df.rename(columns=rename)

    required = [
        "timestamp", "city", "aqi", "co", "no2", "o3", "so2",
        "pm2_5", "pm10", "temperature", "humidity", "pressure",
        "wind_speed", "wind_direction", "clouds",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = (
        df.sort_values(["city", "timestamp"])
        .drop_duplicates(subset=["city", "timestamp"])
        .reset_index(drop=True)
    )
    
    # group = df.groupby("city", group_keys=False)

    numeric = [c for c in required if c not in {"timestamp", "city"}]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    parts = []

    for city, city_df in df.groupby("city", sort=False):
        city_df = city_df.sort_values("timestamp").copy()

        city_df = _add_time_features(city_df)
        city_df = add_lag_features(city_df)
        city_df = add_rolling_features(city_df)
        city_df = add_change_features(city_df)
        city_df = add_targets(city_df)

        parts.append(city_df)

    df = pd.concat(parts, ignore_index=True)

    return df.reset_index(drop=True)
