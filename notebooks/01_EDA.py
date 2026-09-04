from pathlib import Path

import pandas as pd
import plotly.express as px

DATA = Path("feature_repo/data/aqi_features.parquet")
OUT = Path("data/processed/eda")
OUT.mkdir(parents=True, exist_ok=True)

if not DATA.exists():
    raise FileNotFoundError(
        "Run pipelines/backfill_pipeline.py first."
    )

df = pd.read_parquet(DATA)
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df = df.sort_values("timestamp")

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isna().sum().sort_values(ascending=False).head(20))

print("\nDuplicate timestamps:")
print(df.duplicated(["city", "timestamp"]).sum())

print("\nDescriptive statistics:")
print(df[["aqi", "pm2_5", "pm10", "temperature", "humidity"]].describe())

fig = px.line(
    df,
    x="timestamp",
    y="aqi",
    title="AQI over time",
)
fig.write_html(OUT / "aqi_over_time.html")

hourly = (
    df.assign(hour=df["timestamp"].dt.hour)
    .groupby("hour", as_index=False)["aqi"]
    .mean()
)
fig = px.line(
    hourly,
    x="hour",
    y="aqi",
    markers=True,
    title="Mean AQI by hour",
)
fig.write_html(OUT / "aqi_by_hour.html")

monthly = (
    df.assign(month=df["timestamp"].dt.month)
    .groupby("month", as_index=False)["aqi"]
    .mean()
)
fig = px.bar(
    monthly,
    x="month",
    y="aqi",
    title="Mean AQI by month",
)
fig.write_html(OUT / "aqi_by_month.html")

corr_cols = [
    "aqi",
    "pm2_5",
    "pm10",
    "co",
    "no2",
    "o3",
    "so2",
    "temperature",
    "humidity",
    "pressure",
    "wind_speed",
]
corr = df[corr_cols].corr()
corr.to_csv(OUT / "correlation_matrix.csv")

fig = px.imshow(
    corr,
    text_auto=".2f",
    title="Feature correlation matrix",
)
fig.write_html(OUT / "correlation_matrix.html")

print(f"EDA outputs written to {OUT}")
