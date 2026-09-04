from __future__ import annotations

import pandas as pd

from src.config import CITIES
from src.data.api_client import get_current_bundle
from src.features.engineering import engineer_features
from src.features.feature_store import (
    FEATURE_FILE,
    materialize_to_online_store,
    save_feature_dataframe,
)


def main() -> None:
    weather, air = get_current_bundle()

    current = pd.DataFrame(
        [
            {
                "timestamp": pd.to_datetime(
                    air["current"]["time"],
                    utc=True,
                ),
                "city": list(CITIES.keys()),
                "us_aqi": air["current"]["us_aqi"],
                "pm2_5": air["current"]["pm2_5"],
                "pm10": air["current"]["pm10"],
                "carbon_monoxide": air["current"]["carbon_monoxide"],
                "nitrogen_dioxide": air["current"]["nitrogen_dioxide"],
                "sulphur_dioxide": air["current"]["sulphur_dioxide"],
                "ozone": air["current"]["ozone"],
                "temperature_2m": weather["main"]["temp"],
                "relative_humidity_2m": weather["main"]["humidity"],
                "pressure_msl": weather["main"]["pressure"],
                "wind_speed_10m": weather["wind"]["speed"],
                "wind_direction_10m": weather["wind"].get(
                    "deg",
                    0.0,
                ),
                "cloud_cover": weather["clouds"]["all"],
            }
        ]
    )

    if FEATURE_FILE.exists():
        history = pd.read_parquet(FEATURE_FILE)

        # Remove accidental whitespace from existing feature columns.
        history.columns = history.columns.str.strip()

        # Convert the already-engineered data back to the raw columns
        # required by engineer_features so lag/rolling calculations
        # are recalculated.
        raw_columns = [
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

        history = history[raw_columns].rename(
            columns={
                "aqi": "us_aqi",
                "co": "carbon_monoxide",
                "no2": "nitrogen_dioxide",
                "o3": "ozone",
                "so2": "sulphur_dioxide",
                "temperature": "temperature_2m",
                "humidity": "relative_humidity_2m",
                "pressure": "pressure_msl",
                "wind_speed": "wind_speed_10m",
                "wind_direction": "wind_direction_10m",
                "clouds": "cloud_cover",
            }
        )

        combined_raw = pd.concat(
            [history, current],
            ignore_index=True,
        )

    else:
        combined_raw = current

    # Clean all column names.
    combined_raw.columns = combined_raw.columns.str.strip()

    # Remove duplicate observations and sort chronologically
    # independently for each city.
    combined_raw = (
        combined_raw
        .drop_duplicates(
            ["city", "timestamp"]
        )
        .sort_values(
            ["city", "timestamp"]
        )
        .reset_index(drop=True)
    )

    # Generate lag, rolling, change, time and target features.
    features = engineer_features(combined_raw)

    # Save engineered features for training and future pipeline runs.
    save_feature_dataframe(features)

    # Push the latest feature values into Feast's online store.
    materialize_to_online_store()

    print("Hourly feature pipeline completed.")


if __name__ == "__main__":
    main()