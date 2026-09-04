from __future__ import annotations

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from src.config import CITIES


API_URL = "http://127.0.0.1:8080"


st.set_page_config(
    page_title="Pearls AQI Predictor",
    page_icon="🌫️",
    layout="wide",
)

st.title("🌫️ Pearls AQI Predictor")
st.caption("AI-powered Gujrat's air quality forecasting by Huraira Ejaz")


# ---------------------------------------------------------
# City selection
# ---------------------------------------------------------

city = st.selectbox(
    "Select City",
    list(CITIES.keys()),
)


# ---------------------------------------------------------
# API functions
# ---------------------------------------------------------

@st.cache_data(ttl=300)
def load_current(city: str):
    response = requests.get(
        f"{API_URL}/current",
        params={"city": city},
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    return data


@st.cache_data(ttl=300)
def load_predictions(city: str):
    response = requests.get(
        f"{API_URL}/predict",
        params={"city": city},
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    return data


# ---------------------------------------------------------
# Current conditions
# ---------------------------------------------------------

try:

    current_data = load_current(city)

    features = current_data.get("features", {})

    st.caption(
        f"Current conditions for {city}"
    )

except Exception as exc:

    st.error(
        f"Unable to load data for {city}: {exc}"
    )

    st.stop()


def value(name):
    value = features.get(name)

    if value is None:
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def category(aqi: float) -> str:

    if aqi <= 50:
        return "Good"

    if aqi <= 100:
        return "Moderate"

    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    if aqi <= 200:
        return "Unhealthy"

    if aqi <= 300:
        return "Very Unhealthy"

    return "Hazardous"


current_aqi = value("aqi")


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Current AQI",
    round(current_aqi, 1),
)

c2.metric(
    "Category",
    category(current_aqi),
)

c3.metric(
    "PM2.5",
    round(value("pm2_5"), 2),
)

c4.metric(
    "Temperature °C",
    round(value("temperature"), 1),
)


# ---------------------------------------------------------
# Predictions
# ---------------------------------------------------------

st.subheader(
    f"3-day AQI forecast — {city}"
)

try:

    prediction_data = load_predictions(city)

    predictions = prediction_data.get(
        "predictions",
        {},
    )

except Exception as exc:

    st.error(
        f"Prediction failed for {city}: {exc}"
    )

    predictions = {}


forecast_df = pd.DataFrame(
    {
        "Horizon": [
            "24 hours",
            "48 hours",
            "72 hours",
        ],
        "AQI": [
            predictions.get("24h"),
            predictions.get("48h"),
            predictions.get("72h"),
        ],
    }
)


st.dataframe(
    forecast_df,
    width="stretch",
    hide_index=True,
)


valid_forecast = forecast_df.dropna(
    subset=["AQI"]
)


if not valid_forecast.empty:

    fig = px.line(
        valid_forecast,
        x="Horizon",
        y="AQI",
        markers=True,
        title=f"Predicted AQI — {city}",
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )


# ---------------------------------------------------------
# Alerts
# ---------------------------------------------------------

valid_predictions = [
    float(x)
    for x in predictions.values()
    if x is not None
]


max_prediction = max(
    valid_predictions,
    default=0,
)


if max_prediction >= 300:

    st.error(
        "🚨 Hazardous AQI predicted in the next 3 days."
    )

elif max_prediction >= 200:

    st.warning(
        "⚠️ Very unhealthy AQI predicted."
    )

elif max_prediction >= 150:

    st.warning(
        "⚠️ Unhealthy AQI predicted."
    )


# ---------------------------------------------------------
# Pollution
# ---------------------------------------------------------

st.subheader(
    f"Current conditions — {city}"
)


pollution = pd.DataFrame(
    {
        "Pollutant": [
            "PM2.5",
            "PM10",
            "CO",
            "NO₂",
            "O₃",
            "SO₂",
        ],
        "Value": [
            value("pm2_5"),
            value("pm10"),
            value("co"),
            value("no2"),
            value("o3"),
            value("so2"),
        ],
    }
)


st.bar_chart(
    pollution.set_index("Pollutant")
)
