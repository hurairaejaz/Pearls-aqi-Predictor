from __future__ import annotations

import json
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from src.config import FEAST_REPO_PATH, MLFLOW_EXPERIMENT_NAME, MLFLOW_MODEL_NAME
from src.features.feature_store import get_feast_store
from src.models.baseline import persistence_prediction
from src.models.evaluate import regression_metrics
from src.models.features import FEAST_FEATURE_REFS, MODEL_FEATURES, TARGETS
from src.models.random_forest import create_random_forest
from src.models.ridge import create_ridge_model


def load_training_data() -> pd.DataFrame:
    source = Path(FEAST_REPO_PATH) / "data" / "aqi_features.parquet"
    df = pd.read_parquet(source)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], utc=True
    )

    entity_df = df[
        ["city", "timestamp"] + TARGETS
    ].dropna().copy()

    entity_df = entity_df.rename(
        columns={"timestamp": "event_timestamp"}
    )

    store = get_feast_store()

    job = store.get_historical_features(
        entity_df=entity_df,
        features=FEAST_FEATURE_REFS,
    )

    result = job.to_df()

# Feast may return the entity timestamp as either
# "timestamp" or "event_timestamp".
    if "event_timestamp" not in result.columns:
        if "timestamp" in result.columns:
            result = result.rename(
                columns={"timestamp": "event_timestamp"}
            )
        else:
            raise RuntimeError(
                "Feast historical retrieval did not return "
                "timestamp or event_timestamp."
            )

# Keep labels from entity_df.
    label_df = entity_df.copy()

    result = result.merge(
        label_df,
        on=["city", "event_timestamp"],
        how="inner",
        suffixes=("", "_label"),
    )

    for target in TARGETS:
        if target not in result.columns:
            result[target] = result[f"{target}_label"]

    result = result.drop(
        columns=[
            c for c in result.columns
            if c.endswith("_label")
        ],
        errors="ignore",
    )

    return result.sort_values(
        "event_timestamp"
    ).reset_index(drop=True)


def chronological_split(df: pd.DataFrame):
    cutoff = int(len(df) * 0.8)
    return df.iloc[:cutoff].copy(), df.iloc[cutoff:].copy()


def train_horizon(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    horizon: int,
):
    target = f"target_{horizon}h"

    train = train_df.dropna(
        subset=MODEL_FEATURES + [target]
    )
    test = test_df.dropna(
        subset=MODEL_FEATURES + [target]
    )

    X_train = train[MODEL_FEATURES]
    y_train = train[target]

    X_test = test[MODEL_FEATURES]
    y_test = test[target]

    models = {
        "ridge": create_ridge_model(),
        "random_forest": create_random_forest(),
    }

    results = []

    baseline_pred = test["aqi"].map(
        persistence_prediction
    ).to_numpy()

    baseline_metrics = regression_metrics(
        y_test,
        baseline_pred,
    )

    results.append(
        {
            "model": "persistence",
            **baseline_metrics,
        }
    )

    best = None

    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)

        metrics = regression_metrics(
            y_test,
            pred,
        )

        results.append(
            {
                "model": name,
                **metrics,
            }
        )

        if best is None or metrics["rmse"] < best["metrics"]["rmse"]:
            best = {
                "name": name,
                "model": model,
                "metrics": metrics,
            }

    return results, best, X_test, y_test


def register_best(
    model,
    X_sample: pd.DataFrame,
    horizon: int,
    metrics: dict,
    model_type: str,
):
    model_name = f"{MLFLOW_MODEL_NAME}_{horizon}h"

    mlflow.set_tracking_uri(
        __import__("src.config", fromlist=["MLFLOW_TRACKING_URI"]).MLFLOW_TRACKING_URI
    )
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run(
        run_name=f"{model_type}_{horizon}h"
    ):

        mlflow.log_param(
            "horizon_hours",
            horizon,
        )
        mlflow.log_param(
            "model_type",
            model_type,
        )
        mlflow.log_metrics(metrics)

        model_info = mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_sample.head(2),
            registered_model_name=model_name,
        )

        client = mlflow.MlflowClient()
        versions = client.search_model_versions(
            f"name='{model_name}'"
        )
        newest = max(
            versions,
            key=lambda version: int(version.version),
        )

        client.set_registered_model_alias(
            model_name,
            "champion",
            newest.version,
        )

        return model_info.model_uri


def main() -> None:
    df = load_training_data()

    if len(df) < 200:
        raise RuntimeError(
            f"Only {len(df)} usable rows were retrieved. "
            "Run the backfill first and ensure enough hourly history exists."
        )

    train_df, test_df = chronological_split(df)

    all_results = []
    selected = {}

    for horizon in (24, 48, 72):
        results, best, X_test, y_test = train_horizon(
            train_df,
            test_df,
            horizon,
        )

        for row in results:
            row["horizon_hours"] = horizon

        all_results.extend(results)

        if best is None:
            raise RuntimeError(
                f"No trainable model for {horizon}h horizon."
            )

        register_best(
            best["model"],
            X_test,
            horizon,
            best["metrics"],
            best["name"],
        )

        selected[horizon] = {
            "model": best["name"],
            "metrics": best["metrics"],
        }

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(all_results).to_csv(
        output_dir / "model_comparison.csv",
        index=False,
    )

    with open(
        output_dir / "selected_models.json",
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            selected,
            handle,
            indent=2,
        )

    print(
        pd.DataFrame(all_results).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
