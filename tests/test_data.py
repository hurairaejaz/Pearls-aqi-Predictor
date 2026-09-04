import pandas as pd

from src.features.engineering import engineer_features

from src.config import CITIES


def test_supported_cities():

    assert len(CITIES) >= 5

    assert "Gujrat" in CITIES
    assert "Lahore" in CITIES
    assert "Islamabad" in CITIES
    assert "Karachi" in CITIES
    assert "Rawalpindi" in CITIES

def test_city_coordinates():

    for city, config in CITIES.items():

        assert -90 <= config["latitude"] <= 90
        assert -180 <= config["longitude"] <= 180



def test_timestamps_are_utc():
    df = pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:00:00Z"],
            "city": ["Test"],
            "us_aqi": [50],
            "carbon_monoxide": [1],
            "nitrogen_dioxide": [2],
            "ozone": [3],
            "sulphur_dioxide": [4],
            "pm2_5": [5],
            "pm10": [6],
            "temperature_2m": [20],
            "relative_humidity_2m": [50],
            "pressure_msl": [1000],
            "wind_speed_10m": [2],
            "wind_direction_10m": [180],
            "cloud_cover": [20],
        }
    )

    result = engineer_features(df)
    assert str(result["timestamp"].dt.tz) == "UTC"
