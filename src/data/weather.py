import pandas as pd

from src.data.api_client import (
    OpenWeatherClient
)


def parse_current_weather(data):

    main = data.get("main", {})
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})

    rain = data.get("rain", {})

    timestamp = pd.to_datetime(
        data["dt"],
        unit="s",
        utc=True
    )

    return {
        "timestamp": timestamp,

        "temperature": main.get("temp"),
        "feels_like": main.get("feels_like"),

        "pressure": main.get("pressure"),

        "humidity": main.get("humidity"),

        "wind_speed": wind.get("speed"),
        "wind_deg": wind.get("deg"),

        "clouds": clouds.get("all"),

        "rain_1h": rain.get("1h", 0.0),
    }


def get_current_weather():

    client = OpenWeatherClient()

    data = client.current_weather()

    row = parse_current_weather(data)

    return pd.DataFrame([row])


def get_weather_forecast():

    client = OpenWeatherClient()

    data = client.weather_forecast()

    rows = []

    for item in data.get("list", []):

        row = parse_current_weather(item)

        rows.append(row)

    return pd.DataFrame(rows)