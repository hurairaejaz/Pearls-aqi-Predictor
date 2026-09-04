from __future__ import annotations

import traceback

from flask import Flask, jsonify, request
from flask_cors import CORS

from src.config import CITY_NAME, CITIES
from src.features.feature_store import get_latest_online_features
from src.models.predict import predict_from_feature_dict


app = Flask(__name__)

CORS(app)


@app.get("/")
def root():
    return jsonify(
        {
            "name": "Pearls AQI Predictor API",
            "status": "running",
            "default_city": CITY_NAME,
            "available_cities": list(CITIES.keys()),
        }
    )


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "healthy"
        }
    )


@app.get("/cities")
def cities():
    return jsonify(
        {
            "cities": list(CITIES.keys())
        }
    )


@app.get("/current")
def current():

    city = request.args.get(
        "city",
        CITY_NAME,
    )

    if city not in CITIES:
        return jsonify(
            {
                "error": f"Unknown city: {city}",
                "available_cities": list(CITIES.keys()),
            }
        ), 400

    try:

        features = get_latest_online_features(
            city=city
        )

        return jsonify(
            {
                "city": city,
                "features": features,
            }
        )

    except Exception as exc:

        traceback.print_exc()

        return jsonify(
            {
                "error": str(exc),
                "city": city,
            }
        ), 500


@app.get("/predict")
def predict():

    city = request.args.get(
        "city",
        CITY_NAME,
    )

    if city not in CITIES:
        return jsonify(
            {
                "error": f"Unknown city: {city}",
                "available_cities": list(CITIES.keys()),
            }
        ), 400

    try:

        features = get_latest_online_features(
            city=city
        )

        predictions = {}

        for horizon in [24, 48, 72]:

            predictions[f"{horizon}h"] = (
                predict_from_feature_dict(
                    features,
                    horizon,
                )
            )

        return jsonify(
            {
                "city": city,
                "predictions": predictions,
            }
        )

    except Exception as exc:

        traceback.print_exc()

        return jsonify(
            {
                "error": str(exc),
                "city": city,
            }
        ), 500


@app.get("/explain")
def explain():

    return jsonify(
        {
            "message": (
                "Use the Streamlit dashboard for SHAP explanations. "
                "The dashboard loads the registered/production model "
                "and shows feature contributions when the selected "
                "model is tree-based."
            )
        }
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
        use_reloader=False,
    )