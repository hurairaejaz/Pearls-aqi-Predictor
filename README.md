# Pearls AQI Predictor

An end-to-end Air Quality Index (AQI) forecasting application that collects environmental data, engineers machine-learning features, trains a forecasting model, serves predictions through a Flask backend, and displays results in a Streamlit dashboard.

## 1. Project Overview

Pearls AQI Predictor is designed to predict the AQI of a selected city for the next three days. The system combines weather information, air-quality measurements, feature engineering, a feature store, machine-learning inference, and a web interface.

The project was initially configured for **Gujrat, Punjab, Pakistan**, and was later prepared for multi-city support through environment-based configuration.

## 2. Main Objectives

- Collect current and historical weather and air-quality data.
- Store reusable features in a feature repository.
- Generate time-based and environmental features for prediction.
- Train an AQI forecasting model.
- Expose predictions through a Flask REST API.
- Display current conditions and forecasts in a Streamlit dashboard.
- Make the city configurable without changing application code.
- Provide a reproducible local development and testing workflow.

## 3. System Architecture

```text
External Weather/Air-Quality APIs
                |
                v
       Data Collection Layer
                |
                v
       Feature Engineering
                |
                v
       Feature Repository / Feast
                |
                v
       Model Training and Storage
                |
                v
          Flask Backend
                |
                v
       Streamlit Frontend
```

## 4. Technology Stack

- Python
- Flask
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- PyArrow / Parquet
- Feast feature store
- OpenWeather API
- python-dotenv
- Joblib or equivalent model serialization
- PowerShell / virtual environment for local execution

## 5. Project Structure

A typical project structure is:

```text
pearls-aqi-predictor/
│
├── src/
│   ├── api/
│   │   └── app.py
│   ├── data/
│   │   └── ...
│   ├── features/
│   │   └── ...
│   ├── models/
│   │   └── ...
│   └── utils/
│       └── config.py
│
├── feature_repo/
│   ├── data/
│   │   └── aqi_features.parquet
│   └── feature_store.yaml
│
├── frontend/
│   └── app.py
│
├── models/
│   └── ...
│
├── .env
├── requirements.txt
└── README.md
```

The exact filenames may differ depending on the current working tree.

## 6. Configuration

Configuration is loaded from environment variables using `python-dotenv`.

Example `.env`:

```env
OPENWEATHER_API_KEY=your_api_key

CITY_NAME=Gujrat
COUNTRY_CODE=PK
LATITUDE=32.5736
LONGITUDE=74.0789
```

The application should read these values through the central configuration module instead of hard-coding city details in individual files.

Important configuration values include:

- `OPENWEATHER_API_KEY`: API key for external weather and air-quality services.
- `CITY_NAME`: selected city name.
- `COUNTRY_CODE`: country code.
- `LATITUDE`: latitude of the selected city.
- `LONGITUDE`: longitude of the selected city.

For multi-city support, update these variables or introduce a city-selection mechanism that maps each city to its coordinates.

## 7. Installation

### Create a virtual environment

```powershell
python -m venv .venv
```

### Activate it

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file and add the required API key and city configuration.

## 8. Running the Project

### Start the Flask backend

```powershell
python -m src.api.app
```

If the backend file is located elsewhere, run the corresponding Flask entry point.

### Start the Streamlit frontend

Open a second terminal, activate the same virtual environment, and run:

```powershell
streamlit run frontend/app.py
```

The frontend communicates with the Flask backend to retrieve current AQI information and predictions.

## 9. Feature Repository

The project uses a Parquet feature dataset, for example:

```text
feature_repo/data/aqi_features.parquet
```

Typical fields include:

- `city`
- `timestamp`
- `aqi`
- `pm2_5`
- `temperature`
- `humidity`
- Other weather and time-derived features

Example inspection command:

```powershell
python -c "import pandas as pd; p=pd.read_parquet(r'.\feature_repo\data\aqi_features.parquet'); print(p[['city','timestamp','aqi','pm2_5','temperature','humidity']].tail(20).to_string(index=False))"
```

## 10. Model Workflow

The machine-learning workflow consists of:

1. Collecting source data.
2. Cleaning missing or invalid values.
3. Aligning timestamps.
4. Combining air-quality and weather measurements.
5. Creating lag and rolling-window features.
6. Splitting data into training and validation sets.
7. Training the forecasting model.
8. Saving the trained model.
9. Loading the model during API inference.
10. Returning forecast values to the frontend.

## 11. API Responsibilities

The Flask backend is responsible for:

- Health checks.
- Loading configuration.
- Loading the trained model.
- Reading recent feature values.
- Generating predictions.
- Returning JSON responses.
- Handling invalid requests and missing data.
- Providing a stable interface for the Streamlit dashboard.

A typical response may contain:

```json
{
  "city": "Gujrat",
  "current_aqi": 85,
  "forecast": [
    {
      "date": "2026-09-06",
      "predicted_aqi": 92
    }
  ]
}
```

The exact endpoint names and response schema depend on the current Flask implementation.

## 12. Frontend Responsibilities

The Streamlit application provides:

- City and forecast information.
- Current AQI display.
- Weather indicators.
- Forecast values.
- Tables or charts for predicted AQI.
- User-friendly error messages.
- A simple interface for non-technical users.

## 13. Multi-City Readiness

The project was originally centered on Gujrat. To support multiple cities correctly:

- Avoid importing fixed city values into modules that need dynamic city selection.
- Keep city name, country code, latitude, and longitude together.
- Store the city identifier with every feature record.
- Filter feature data by city before prediction.
- Ensure the model receives features from the selected city.
- Avoid using Gujrat as an unintended fallback.
- Update frontend controls to let users select a city.
- Validate that every supported city has valid coordinates and data.

## 14. Testing

Useful checks include:

```powershell
python -c "import pandas as pd; p=pd.read_parquet(r'.\feature_repo\data\aqi_features.parquet'); print(p.shape); print(p.columns.tolist())"
```

Check the latest records:

```powershell
python -c "import pandas as pd; p=pd.read_parquet(r'.\feature_repo\data\aqi_features.parquet'); print(p.tail().to_string(index=False))"
```

Check that the backend starts:

```powershell
python -m src.api.app
```

Check that the frontend starts:

```powershell
streamlit run frontend/app.py
```

## 15. Common Issues

### API key missing

Verify that `.env` exists and contains `OPENWEATHER_API_KEY`.

### Wrong city displayed

Check all hard-coded references to Gujrat and ensure the application uses the central configuration module.

### Empty predictions

Verify that the feature dataset contains recent records and that the model expects the same feature columns produced by the pipeline.

### Backend connection error

Start Flask before opening the Streamlit frontend and verify the backend URL configured in the frontend.

### Feature-store errors

Check the Feast repository configuration, feature definitions, entity keys, timestamps, and Parquet path.

## 16. Future Improvements

- Add a complete city selector.
- Add automated scheduled data ingestion.
- Add model retraining.
- Add model evaluation metrics.
- Add prediction confidence intervals.
- Add historical AQI charts.
- Add database-backed storage.
- Add Docker support.
- Add CI/CD.
- Add automated unit and integration tests.
- Add monitoring for data drift and API failures.


## 17. Complete Technology and Deployment Stack

The project uses the following components:

| Component | Purpose |
|---|---|
| OpenWeather | Live weather data |
| Open-Meteo | Historical and current air-quality and pollutant data |
| Feast | Feature Store for consistent training and inference features |
| Pandas / NumPy | Data processing and feature engineering |
| Scikit-learn | Ridge Regression and Random Forest models |
| TensorFlow | LSTM deep-learning experiment |
| MLflow | Experiment tracking and model registry |
| SHAP | Model explainability |
| Flask | REST API backend |
| Streamlit | Interactive dashboard |
| GitHub Actions | Automation and CI/CD workflows |
| Docker | Containerization |
| Google Cloud Run | Cloud deployment target |

## 18. Important Data-Source Decision

OpenWeather's standard Air Pollution API returns an AQI index on a **1–5 scale**. This project instead predicts a continuous **US-AQI-style value**, making RMSE, MAE, R², and 24/48/72-hour forecasts meaningful.

Therefore:

- Historical and live AQI/pollutant data are collected from Open-Meteo's air-quality API.
- Live weather data are collected from OpenWeather.
- The model target is a continuous AQI-style value.
- The Feast, model, Flask, and Streamlit interfaces are designed to remain independent of the upstream AQI provider.

If an OpenWeather historical endpoint becomes available that returns the exact AQI scale required by the project, the historical backfill client can be replaced without redesigning the downstream interfaces.

## 19. Complete First-Run Workflow

Use Python 3.11.

### Create and activate the environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configure environment variables

Copy `.env.example` to `.env` and add the OpenWeather API key and project location.

### Backfill historical data

```powershell
python pipelines/backfill_pipeline.py
```

### Register Feast definitions

```powershell
cd feature_repo
feast apply
cd ..
```

### Train the tabular models

```powershell
python pipelines/training_pipeline.py
```

### Materialize the latest features

```powershell
python pipelines/feature_pipeline.py
```

### Start MLflow

```powershell
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db
```

### Start Flask

In another terminal:

```powershell
python -m api.app
```

### Start Streamlit

In another terminal:

```powershell
streamlit run dashboard/app.py
```

## 20. Exploratory Data Analysis

After the historical backfill is complete, run:

```powershell
python notebooks/01_EDA.py
```

Generated HTML reports are stored under:

```text
data/processed/eda/
```

These reports help inspect data distributions, missing values, time trends, pollutant behavior, and relationships between weather variables and AQI.

## 21. Forecasting Definition

The forecasting problem uses features at time `t` to predict future AQI values:

```text
target_24h = AQI(t + 24 hours)
target_48h = AQI(t + 48 hours)
target_72h = AQI(t + 72 hours)
```

The training split is chronological. This prevents future observations from leaking into the training set and producing unrealistically optimistic evaluation results.

## 22. Model Evaluation

The training pipeline evaluates:

- Persistence baseline.
- Ridge Regression.
- Random Forest.

The primary evaluation metrics are:

- **RMSE:** Measures the square-root average prediction error and penalizes larger errors.
- **MAE:** Measures the average absolute prediction error.
- **R²:** Measures the proportion of target variance explained by the model.

The TensorFlow/LSTM module is included as a deep-learning experiment and can be trained using the same chronological forecasting dataset.

## 23. Explainability and Experiment Tracking

MLflow is used to track experiments, parameters, metrics, and model artifacts. The model registry can be used to manage selected model versions for deployment.

SHAP is included to explain model predictions and identify which features contribute most strongly to AQI forecasts. This improves transparency and helps diagnose unexpected predictions.

## 24. Deployment

The API can be containerized with Docker:

```powershell
docker build -t pearls-aqi-api .
```

The resulting container can be deployed to Google Cloud Run after configuring:

- Google Cloud project.
- Container registry or artifact repository.
- Runtime environment variables.
- API secrets.
- Required service permissions.

The deployment process should keep secrets outside the image and inject them through the cloud environment.

## 25. Security and Repository Hygiene

Do not commit the following files or values:

- `.env`
- OpenWeather API keys
- MLflow databases
- Feast databases
- Trained model artifacts
- Local credentials
- Other private deployment secrets

Use `.gitignore`, environment variables, and cloud secret management to protect sensitive configuration.
