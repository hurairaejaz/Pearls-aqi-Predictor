from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64, String

aqi_source = FileSource(
    name="aqi_features_source",
    path="data/aqi_features.parquet",
    timestamp_field="timestamp",
)

city = Entity(
    name="city",
    join_keys=["city"],
    description="City used as the AQI prediction entity.",
)

aqi_features = FeatureView(
    name="aqi_features",
    entities=[city],
    ttl=timedelta(days=30),
    source=aqi_source,
    schema=[
        Field(name="aqi", dtype=Float32),
        Field(name="co", dtype=Float32),
        Field(name="no2", dtype=Float32),
        Field(name="o3", dtype=Float32),
        Field(name="so2", dtype=Float32),
        Field(name="pm2_5", dtype=Float32),
        Field(name="pm10", dtype=Float32),
        Field(name="temperature", dtype=Float32),
        Field(name="humidity", dtype=Float32),
        Field(name="pressure", dtype=Float32),
        Field(name="wind_speed", dtype=Float32),
        Field(name="wind_direction", dtype=Float32),
        Field(name="clouds", dtype=Float32),
        Field(name="hour", dtype=Int64),
        Field(name="day", dtype=Int64),
        Field(name="day_of_week", dtype=Int64),
        Field(name="month", dtype=Int64),
        Field(name="week", dtype=Int64),
        Field(name="is_weekend", dtype=Int64),
        Field(name="hour_sin", dtype=Float32),
        Field(name="hour_cos", dtype=Float32),
        Field(name="month_sin", dtype=Float32),
        Field(name="month_cos", dtype=Float32),
        Field(name="aqi_lag_1h", dtype=Float32),
        Field(name="aqi_lag_3h", dtype=Float32),
        Field(name="aqi_lag_6h", dtype=Float32),
        Field(name="aqi_lag_12h", dtype=Float32),
        Field(name="aqi_lag_24h", dtype=Float32),
        Field(name="pm25_lag_1h", dtype=Float32),
        Field(name="pm25_lag_3h", dtype=Float32),
        Field(name="pm25_lag_6h", dtype=Float32),
        Field(name="pm25_lag_12h", dtype=Float32),
        Field(name="pm25_lag_24h", dtype=Float32),
        Field(name="aqi_rolling_3h", dtype=Float32),
        Field(name="aqi_rolling_6h", dtype=Float32),
        Field(name="aqi_rolling_12h", dtype=Float32),
        Field(name="aqi_rolling_24h", dtype=Float32),
        Field(name="pm25_rolling_6h", dtype=Float32),
        Field(name="pm25_rolling_24h", dtype=Float32),
        Field(name="aqi_change", dtype=Float32),
        Field(name="aqi_percentage_change", dtype=Float32),
        Field(name="pm25_change", dtype=Float32),
        Field(name="temperature_change", dtype=Float32),
        Field(name="humidity_change", dtype=Float32),
    ],
)
