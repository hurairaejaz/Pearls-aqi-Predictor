# Pearls AQI Predictor

End-to-end AQI forecasting system using:

- OpenWeather for live weather data
- Open-Meteo historical/current air-quality data for a continuous US-AQI target
- Feast Feature Store
- Scikit-learn (Ridge + Random Forest)
- TensorFlow/LSTM experiment
- MLflow experiment tracking and model registry
- SHAP explainability
- Flask REST API
- Streamlit dashboard
- GitHub Actions automation
- Docker / Cloud Run deployment

## Important data-source decision

OpenWeather's standard Air Pollution API returns an AQI index on a 1–5 scale. This project predicts a continuous US-AQI-style value so that RMSE/MAE/R² and 24/48/72-hour forecasts are meaningful. Therefore historical and live AQI/pollutant data use Open-Meteo's air-quality API, while live weather is collected from OpenWeather.

If your OpenWeather account provides a historical endpoint that returns the exact AQI scale you want to use, the backfill client can be replaced without changing the Feast/model/dashboard interfaces.

## Setup

Use Python 3.11.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your OpenWeather API key and project location.

## First run

1. Backfill historical data:

```powershell
python pipelines/backfill_pipeline.py
```

2. Register Feast definitions:

```powershell
cd feature_repo
feast apply
cd ..
```

3. Train the tabular models:

```powershell
python pipelines/training_pipeline.py
```

4. Materialize the latest features:

```powershell
python pipelines/feature_pipeline.py
```

5. Start MLflow:

```powershell
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db
```

6. Start Flask in another terminal:

```powershell
python -m api.app
```

7. Start Streamlit in another terminal:

```powershell
streamlit run dashboard/app.py
```

## Feast

The Feature Store repository is `feature_repo/`.

```powershell
cd feature_repo
feast apply
feast feature-views list
```

The local provider uses a SQLite online store and Parquet batch source.

## EDA

After backfill:

```powershell
python notebooks/01_EDA.py
```

Open the generated HTML files under `data/processed/eda/`.

## Forecasting problem

Features at time `t` predict:

- `target_24h = AQI(t+24h)`
- `target_48h = AQI(t+48h)`
- `target_72h = AQI(t+72h)`

The training split is chronological to prevent future leakage.

## Model evaluation

The pipeline evaluates:

- persistence baseline
- Ridge regression
- Random Forest

Metrics:

- RMSE
- MAE
- R²

The TensorFlow LSTM module is included for the deep-learning experiment and can be trained as an extension of the same chronological dataset.

## Project structure

See the repository tree in the project report. The important flow is:

OpenWeather/Open-Meteo -> feature engineering -> Feast -> historical retrieval -> training -> MLflow Registry -> Flask -> Streamlit.

## Deployment

Build the API:

```powershell
docker build -t pearls-aqi-api .
```

Then deploy the container to Cloud Run after configuring your cloud project and secrets.

Do not commit `.env`, MLflow databases, Feast databases, trained models, or API keys.
