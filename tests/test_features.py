import pandas as pd

from src.features.engineering import engineer_features


def test_engineer_features_creates_targets():
    timestamps = pd.date_range(
        "2026-01-01",
        periods=100,
        freq="h",
        tz="UTC",
    )

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "city": ["Test"] * 100,
            "us_aqi": range(100),
            "carbon_monoxide": [1.0] * 100,
            "nitrogen_dioxide": [2.0] * 100,
            "ozone": [3.0] * 100,
            "sulphur_dioxide": [4.0] * 100,
            "pm2_5": [5.0] * 100,
            "pm10": [6.0] * 100,
            "temperature_2m": [20.0] * 100,
            "relative_humidity_2m": [60.0] * 100,
            "pressure_msl": [1000.0] * 100,
            "wind_speed_10m": [3.0] * 100,
            "wind_direction_10m": [180.0] * 100,
            "cloud_cover": [30.0] * 100,
        }
    )

    result = engineer_features(df)

    assert "target_24h" in result.columns
    assert "target_48h" in result.columns
    assert "target_72h" in result.columns
    assert "aqi_lag_24h" in result.columns
    assert "aqi_rolling_24h" in result.columns

    assert result["target_24h"].iloc[0] == 24
