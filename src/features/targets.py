import pandas as pd


def create_targets(df):

    df = df.sort_values("timestamp").copy()

    df["target_24h"] = (
        df["aqi"].shift(-24)
    )

    df["target_48h"] = (
        df["aqi"].shift(-48)
    )

    df["target_72h"] = (
        df["aqi"].shift(-72)
    )

    return df

def create_lag_features(df):

    df = df.sort_values("timestamp").copy()

    lag_hours = [1, 3, 6, 12, 24]

    for lag in lag_hours:

        df[f"aqi_lag_{lag}h"] = (
            df["aqi"].shift(lag)
        )

        df[f"pm25_lag_{lag}h"] = (
            df["pm2_5"].shift(lag)
        )

    return df

def create_rolling_features(df):

    df = df.sort_values("timestamp").copy()

    df["aqi_rolling_3h"] = (
        df["aqi"]
        .rolling(3)
        .mean()
    )

    df["aqi_rolling_6h"] = (
        df["aqi"]
        .rolling(6)
        .mean()
    )

    df["aqi_rolling_12h"] = (
        df["aqi"]
        .rolling(12)
        .mean()
    )

    df["aqi_rolling_24h"] = (
        df["aqi"]
        .rolling(24)
        .mean()
    )

    df["pm25_rolling_6h"] = (
        df["pm2_5"]
        .rolling(6)
        .mean()
    )

    df["pm25_rolling_24h"] = (
        df["pm2_5"]
        .rolling(24)
        .mean()
    )

    return df