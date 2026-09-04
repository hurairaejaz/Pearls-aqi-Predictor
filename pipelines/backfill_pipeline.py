from __future__ import annotations

from datetime import datetime, timedelta, timezone
from src.config import CITIES
from src.config import BACKFILL_DAYS, RAW_DIR
from src.data.api_client import get_historical_open_meteo
from src.features.engineering import engineer_features
from src.features.feature_store import save_feature_dataframe
import pandas as pd

def main() -> None:
    end = datetime.now(timezone.utc).date() - timedelta(days=2)
    start = end - timedelta(days=BACKFILL_DAYS - 1)

    print(f"Backfilling {start} -> {end}")

    raw = get_historical_open_meteo(
        start.isoformat(),
        end.isoformat(),
    )

    raw_path = RAW_DIR / "historical_open_meteo.parquet"
    raw.to_parquet(raw_path, index=False)

    features = engineer_features(raw)
    feature_path = save_feature_dataframe(features)

    print(f"Raw data: {raw_path}")
    print(f"Feature data: {feature_path}")
    print(f"Rows: {len(features)}")


if __name__ == "__main__":
    main()

end_date = (
    datetime.now(timezone.utc).date()
    - timedelta(days=2)
)

start_date = (
    end_date
    - timedelta(days=BACKFILL_DAYS - 1)
)

start_date = start_date.isoformat()
end_date = end_date.isoformat()


all_city_data = []

for city, config in CITIES.items():

    print(
        f"Fetching {city} "
        f"({config['latitude']}, "
        f"{config['longitude']})"
    )

    city_df = get_historical_open_meteo(
        start_date=start_date,
        end_date=end_date,
        latitude=config["latitude"],
        longitude=config["longitude"],
        city=city,
    )

    all_city_data.append(city_df)


raw_df = pd.concat(
    all_city_data,
    ignore_index=True,
)

raw_df = raw_df.sort_values(
    ["city", "timestamp"]
)

features_df = engineer_features(
    raw_df
)


raw_df.to_parquet(
    raw_path,
    index=False,
)

features_df.to_parquet(
    feature_path,
    index=False,
)