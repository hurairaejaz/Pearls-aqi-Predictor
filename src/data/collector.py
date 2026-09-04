import pandas as pd

from src.data.weather import (
    get_current_weather
)

from src.data.pollution import (
    get_current_pollution
)


def collect_current_data():

    weather = get_current_weather()

    pollution = get_current_pollution()

    df = pd.merge(
        weather,
        pollution,
        on="timestamp",
        how="outer"
    )

    df = df.sort_values(
        "timestamp"
    )

    return df


if __name__ == "__main__":

    df = collect_current_data()

    print(
        "\nCollected data:\n"
    )

    print(
        df.to_string(index=False)
    )