from __future__ import annotations

import pandas as pd
import requests

from src.config import (
    AIR_QUALITY_PROVIDER,
    CITY_NAME,
    LATITUDE,
    LONGITUDE,
    OPENWEATHER_API_KEY,
)


OPENWEATHER_BASE = (
    "https://api.openweathermap.org/data/2.5"
)

OPEN_METEO_WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)

OPEN_METEO_ARCHIVE_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)

OPEN_METEO_AIR_URL = (
    "https://air-quality-api.open-meteo.com/v1/air-quality"
)


def _get_json(
    url: str,
    params: dict,
) -> dict:

    response = requests.get(
        url,
        params=params,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def get_current_weather_openweather() -> dict:

    params = {
        "lat": LATITUDE,
        "lon": LONGITUDE,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    return _get_json(
        f"{OPENWEATHER_BASE}/weather",
        params,
    )


def get_current_air_quality_open_meteo() -> dict:

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": (
            "us_aqi,pm2_5,pm10,"
            "carbon_monoxide,nitrogen_dioxide,"
            "sulphur_dioxide,ozone"
        ),
        "timezone": "UTC",
    }

    return _get_json(
        OPEN_METEO_AIR_URL,
        params,
    )


def get_current_weather_open_meteo() -> dict:

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "pressure_msl,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "cloud_cover"
        ),
        "timezone": "UTC",
    }

    return _get_json(
        OPEN_METEO_WEATHER_URL,
        params,
    )


def get_current_bundle() -> tuple[dict, dict]:

    weather = get_current_weather_openweather()

    if AIR_QUALITY_PROVIDER != "open_meteo":
        raise ValueError(
            "This implementation supports "
            "AIR_QUALITY_PROVIDER=open_meteo."
        )

    pollution = get_current_air_quality_open_meteo()

    return weather, pollution


def get_historical_open_meteo(
    start_date: str,
    end_date: str,
    latitude: float | None = None,
    longitude: float | None = None,
    city: str | None = None,
) -> pd.DataFrame:

    latitude = (
        LATITUDE
        if latitude is None
        else latitude
    )

    longitude = (
        LONGITUDE
        if longitude is None
        else longitude
    )

    city = (
        CITY_NAME
        if city is None
        else city
    )

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "pressure_msl,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "cloud_cover"
        ),
        "timezone": "UTC",
    }

    air_params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": (
            "us_aqi,"
            "pm2_5,"
            "pm10,"
            "carbon_monoxide,"
            "nitrogen_dioxide,"
            "sulphur_dioxide,"
            "ozone"
        ),
        "timezone": "UTC",
    }

    weather = _get_json(
        OPEN_METEO_ARCHIVE_URL,
        weather_params,
    )

    air = _get_json(
        OPEN_METEO_AIR_URL,
        air_params,
    )

    weather_df = pd.DataFrame(
        weather["hourly"]
    )

    air_df = pd.DataFrame(
        air["hourly"]
    )

    weather_df["timestamp"] = pd.to_datetime(
        weather_df["time"],
        utc=True,
    )

    air_df["timestamp"] = pd.to_datetime(
        air_df["time"],
        utc=True,
    )

    weather_df = weather_df.drop(
        columns=["time"]
    )

    air_df = air_df.drop(
        columns=["time"]
    )

    df = weather_df.merge(
        air_df,
        on="timestamp",
        how="inner",
    )

    df["city"] = city
    df["latitude"] = latitude
    df["longitude"] = longitude

    return df