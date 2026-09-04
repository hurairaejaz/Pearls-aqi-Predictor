import pandas as pd

from src.data.api_client import (
    OpenWeatherClient
)


POLLUTANT_COLUMNS = [
    "co",
    "no",
    "no2",
    "o3",
    "so2",
    "pm2_5",
    "pm10",
    "nh3",
]


def parse_pollution_item(item):

    components = item.get(
        "components",
        {}
    )

    main = item.get(
        "main",
        {}
    )

    timestamp = pd.to_datetime(
        item["dt"],
        unit="s",
        utc=True
    )

    row = {
        "timestamp": timestamp,

        "aqi": main.get("aqi"),

        "co": components.get("co"),
        "no": components.get("no"),
        "no2": components.get("no2"),
        "o3": components.get("o3"),
        "so2": components.get("so2"),

        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),

        "nh3": components.get("nh3"),
    }

    return row


def get_current_pollution():

    client = OpenWeatherClient()

    data = client.current_pollution()

    rows = []

    for item in data.get(
        "list",
        []
    ):

        rows.append(
            parse_pollution_item(item)
        )

    return pd.DataFrame(rows)


def get_pollution_forecast():

    client = OpenWeatherClient()

    data = client.pollution_forecast()

    rows = []

    for item in data.get(
        "list",
        []
    ):

        rows.append(
            parse_pollution_item(item)
        )

    return pd.DataFrame(rows)