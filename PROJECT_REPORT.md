# Pearls AQI Predictor
## Detailed Project Achievement Report

### 1. Executive Summary

Pearls AQI Predictor is an end-to-end machine-learning application developed to forecast Air Quality Index values for the next three days. The project integrates data collection, feature engineering, feature storage, model training, backend inference, and frontend visualization into one workflow.

The implementation established the foundation of a complete AQI prediction platform. It moved the project beyond a standalone model by connecting the data pipeline to a Flask API and a Streamlit dashboard. The system was initially configured for Gujrat, Punjab, Pakistan, and the configuration was subsequently examined and prepared for expansion to multiple cities.

### 2. Project Goals

The major goals were:

1. Build a complete AQI prediction pipeline.
2. Collect weather and air-quality information from external services.
3. Prepare reliable machine-learning features.
4. Store features in a reusable feature repository.
5. Train and persist a forecasting model.
6. Serve predictions through a Flask backend.
7. Present current AQI and forecasts through Streamlit.
8. Make the system configurable and easier to extend.
9. Establish commands and checks for local testing.
10. Identify and remove city-specific assumptions for multi-city support.

### 3. Work Completed

#### 3.1 Environment and Configuration

A centralized configuration approach was established using environment variables and `python-dotenv`.

The configuration includes:

- OpenWeather API key.
- City name.
- Country code.
- Latitude.
- Longitude.

This approach separates secrets and deployment-specific settings from application code. It also makes it possible to change the target city without editing multiple source files.

The project was initially configured with Gujrat as the default city. The relevant configuration values were identified so that the application could later support multiple cities.

#### 3.2 Data Collection Foundation

The project was structured around collecting external environmental data. Weather and air-quality information is required because AQI is influenced by particulate matter and meteorological conditions such as temperature and humidity.

The data collection process is intended to:

- Request data from external APIs.
- Parse API responses.
- Normalize the values.
- Attach timestamps.
- Associate each observation with a city.
- Save the resulting records for downstream processing.

This creates the foundation for both historical training data and current prediction inputs.

#### 3.3 Feature Engineering

The project includes a feature-engineering stage that transforms raw observations into model-ready data.

The feature dataset includes fields such as:

- City.
- Timestamp.
- AQI.
- PM2.5.
- Temperature.
- Humidity.

The feature-engineering stage is responsible for making data consistent and useful for forecasting. Depending on the current implementation, this may include time-based features, lagged AQI values, rolling statistics, weather variables, missing-value handling, and feature alignment.

A key achievement was the creation and inspection of a Parquet feature dataset:

```text
feature_repo/data/aqi_features.parquet
```

The dataset can be inspected with Pandas, confirming that the pipeline produces structured records rather than unorganized API responses.

#### 3.4 Feature Repository and Feast Integration

The project uses a feature repository structure and Feast-related configuration.

This is important because a feature store provides a consistent way to define, retrieve, and reuse features for training and inference. It also helps reduce the risk of training-serving skew, where the model is trained on one representation of the data but receives a different representation during prediction.

The feature repository provides a clear separation between:

- Raw data collection.
- Feature definitions.
- Stored feature values.
- Model input data.

#### 3.5 Machine-Learning Pipeline

The project includes the main components required for an AQI forecasting workflow:

1. Data preparation.
2. Feature generation.
3. Training-data construction.
4. Model training.
5. Model persistence.
6. Model loading during inference.
7. Prediction generation.

The intended forecast horizon is three days. The model uses environmental and historical information to estimate future AQI values.

Persisting the trained model is a major achievement because it allows the API to generate predictions without retraining the model for every request.

#### 3.6 Flask Backend

A Flask backend was established as the service layer between the machine-learning pipeline and the user interface.

The backend is responsible for:

- Starting the application server.
- Loading configuration.
- Loading the trained model.
- Reading the latest feature data.
- Preparing prediction inputs.
- Generating forecasts.
- Returning results to the frontend.
- Handling service-level errors.

This creates a clean separation between the prediction logic and the presentation layer.

The frontend does not need to know how the model works internally. It only needs to request prediction data from the backend.

#### 3.7 Streamlit Frontend

A Streamlit frontend was established to make the project accessible through a simple dashboard.

The frontend is intended to show:

- Selected city.
- Current AQI.
- Weather conditions.
- Predicted AQI values.
- Forecast information.
- Readable tables and visual summaries.

Using Streamlit makes it possible to demonstrate the project without building a separate JavaScript application.

#### 3.8 Local Execution Workflow

A repeatable local workflow was documented.

The project uses a Python virtual environment and separate processes for the backend and frontend.

Backend command:

```powershell
python -m src.api.app
```

Frontend command:

```powershell
streamlit run frontend/app.py
```

This separation allows the Flask service to run independently while Streamlit acts as the client.

#### 3.9 Data Validation and Testing

The feature dataset was inspected using Pandas commands. These checks help verify:

- The Parquet file exists.
- The dataset can be loaded.
- Expected columns are present.
- Recent records are available.
- City and timestamp values are populated.
- AQI and environmental measurements are being generated.

Example:

```powershell
python -c "import pandas as pd; p=pd.read_parquet(r'.\feature_repo\data\aqi_features.parquet'); print(p[['city','timestamp','aqi','pm2_5','temperature','humidity']].tail(20).to_string(index=False))"
```

These checks are useful for debugging ingestion, feature engineering, and prediction failures.

### 4. Important Files and Their Responsibilities

| File or directory | Responsibility |
|---|---|
| `src/utils/config.py` | Loads environment variables and central configuration |
| `.env` | Stores API keys and city-specific settings |
| `feature_repo/` | Contains feature-store configuration and feature data |
| `feature_repo/data/aqi_features.parquet` | Stores engineered AQI feature records |
| Flask application module | Exposes prediction services through HTTP |
| Streamlit application module | Displays AQI and forecast information |
| Model directory | Stores trained model artifacts |
| Requirements file | Defines Python dependencies |

The exact names may vary slightly in the current repository, but these are the principal architectural responsibilities.

### 5. Original Gujrat Configuration

The application was initially designed around Gujrat. The following values were used as the original defaults:

- City: Gujrat.
- Country: Pakistan.
- Latitude: approximately 32.5736.
- Longitude: approximately 74.0789.

This was suitable for the first version but created a limitation: some parts of the application could unintentionally remain tied to Gujrat even after configuration values were changed.

A major part of the later work was identifying where values such as:

```python
from src.utils.config import CITY_NAME, LATITUDE, LONGITUDE
```

were imported and where Gujrat-specific assumptions could still exist.

### 6. Multi-City Support Preparation

The project was reviewed for multi-city support. The key technical changes required are:

- Use configuration values rather than hard-coded city names.
- Pass city information through the complete data pipeline.
- Store city identifiers with feature records.
- Filter records by the selected city.
- Use the selected city's coordinates when calling external APIs.
- Ensure prediction inputs are generated for the selected city.
- Update the frontend to allow city selection.
- Avoid using Gujrat as an unintended fallback.
- Validate that each city has enough historical data.

This work improves maintainability and makes the system suitable for deployment beyond one location.

### 7. Current System Flow

The complete intended flow is:

```text
1. User opens Streamlit dashboard
2. Frontend requests data from Flask
3. Flask loads configuration and model
4. Backend obtains recent feature values
5. Features are prepared for inference
6. Model generates AQI forecast
7. Flask returns JSON response
8. Streamlit displays current AQI and forecast
```

For data updates, the upstream flow is:

```text
External APIs
    ↓
Data ingestion
    ↓
Cleaning and normalization
    ↓
Feature engineering
    ↓
Parquet / Feast repository
    ↓
Training or inference
```

### 8. Achievements

The following outcomes were achieved:

- Designed an end-to-end AQI prediction architecture.
- Established environment-based configuration.
- Integrated the project with external environmental data sources.
- Created a structured feature dataset.
- Added a feature repository approach using Parquet and Feast concepts.
- Built the foundation for model training and prediction.
- Established model persistence for inference.
- Implemented a Flask backend layer.
- Implemented a Streamlit frontend layer.
- Documented backend and frontend startup commands.
- Added practical dataset inspection commands.
- Investigated city-specific configuration dependencies.
- Prepared the project for multi-city expansion.
- Identified common failure points and testing requirements.

### 9. Technical Benefits

#### Maintainability

Centralized configuration reduces duplicated settings and makes changes easier.

#### Reusability

The feature repository allows the same engineered features to be used by training and inference.

#### Scalability

Separating the backend and frontend makes it easier to deploy each component independently.

#### Extensibility

The architecture can be expanded with more cities, more weather variables, improved models, and additional dashboards.

#### Reproducibility

The documented environment and execution commands make it easier to run the project consistently.

### 10. Limitations

The current implementation still has areas that require additional work:

- The initial data and configuration are centered on Gujrat.
- Multi-city selection may require additional frontend and backend changes.
- Forecast quality depends on the quantity and quality of historical data.
- External API availability can affect data collection.
- Model performance metrics should be documented more formally.
- Automated tests should be expanded.
- Production deployment and monitoring are not yet fully implemented.
- The exact API contract should be documented and versioned.
- Data drift and model degradation monitoring should be added.

### 11. Recommended Future Enhancements

1. Add a city configuration file or database.
2. Add a city selector to Streamlit.
3. Add city-aware feature retrieval.
4. Add scheduled ingestion using a task scheduler.
5. Add automated model retraining.
6. Add MAE, RMSE, and R² evaluation metrics.
7. Add historical-versus-predicted AQI charts.
8. Add confidence intervals.
9. Add API authentication and rate limiting.
10. Add structured logging.
11. Add unit and integration tests.
12. Add Docker and deployment configuration.
13. Add monitoring for missing data and API failures.
14. Add model versioning.
15. Add documentation for all API endpoints.

### 12. Conclusion

Pearls AQI Predictor successfully established the core components of a complete AQI forecasting application. The project combines data collection, feature engineering, feature storage, machine learning, Flask-based inference, and a Streamlit dashboard.

The most important achievement is the transition from an isolated prediction concept to an integrated application that can collect data, prepare features, generate predictions, and present results to users.

The project is now positioned for the next stage: completing robust multi-city support, improving model evaluation, automating data updates, and preparing the system for production deployment.


## 13. Expanded Technology Stack and Data-Source Design

The completed project uses a broader production-oriented stack than a basic AQI dashboard.

### Data providers

- **OpenWeather** supplies live weather information.
- **Open-Meteo** supplies historical and current air-quality and pollutant information.

This separation was an important design decision. OpenWeather's standard Air Pollution API uses a 1–5 AQI index, while the project requires a continuous US-AQI-style target for meaningful regression metrics and multi-hour forecasting.

### Machine learning

- Ridge Regression provides a regularized linear baseline.
- Random Forest provides a nonlinear tabular model.
- TensorFlow/LSTM provides an experimental deep-learning approach.

### MLOps and explainability

- Feast manages reusable features.
- MLflow tracks experiments and stores model versions.
- SHAP supports model interpretation.

### Application and deployment

- Flask exposes predictions through REST endpoints.
- Streamlit provides the dashboard.
- GitHub Actions supports automation.
- Docker packages the API.
- Google Cloud Run is the intended deployment platform.

## 14. Exact Forecasting Targets

The project defines three future prediction targets:

```text
target_24h = AQI(t + 24h)
target_48h = AQI(t + 48h)
target_72h = AQI(t + 72h)
```

A chronological split is used for training and evaluation. This is essential for time-series forecasting because random splitting could allow future information to influence training.

## 15. Model Evaluation and Experimentation

The project evaluates a persistence baseline, Ridge Regression, and Random Forest using:

- RMSE.
- MAE.
- R².

The persistence baseline provides a reference point by estimating future AQI from recent observed AQI. The tabular models are then compared against this baseline.

The TensorFlow/LSTM implementation extends the project into deep-learning experimentation. MLflow provides a consistent place to record model parameters, evaluation metrics, artifacts, and registered model versions.

SHAP adds interpretability by showing which environmental and historical features influence individual predictions.

## 16. Exploratory Data Analysis

The EDA workflow is executed with:

```powershell
python notebooks/01_EDA.py
```

The generated HTML reports are stored in:

```text
data/processed/eda/
```

EDA supports the project by helping identify:

- Missing observations.
- Outliers.
- AQI trends.
- Pollutant distributions.
- Weather/AQI relationships.
- Potential data-quality problems.
- Seasonal or time-based patterns.

## 17. Reproducible First-Run Procedure

The complete first-run process is:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure `.env`, then run:

```powershell
python pipelines/backfill_pipeline.py
```

Register the feature definitions:

```powershell
cd feature_repo
feast apply
cd ..
```

Train the models:

```powershell
python pipelines/training_pipeline.py
```

Materialize the latest features:

```powershell
python pipelines/feature_pipeline.py
```

Start MLflow:

```powershell
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db
```

Start the API:

```powershell
python -m api.app
```

Start the dashboard:

```powershell
streamlit run dashboard/app.py
```

## 18. Deployment and Automation

The project includes deployment preparation through Docker and Cloud Run:

```powershell
docker build -t pearls-aqi-api .
```

GitHub Actions is intended to automate validation, testing, and deployment-related workflows. Cloud Run provides a serverless container execution target for the Flask API.

Production deployment requires cloud configuration, environment variables, secrets, service permissions, and a configured container registry.

## 19. Expanded Achievement Summary

In addition to the core pipeline, the project now includes or is prepared for:

- Continuous US-AQI-style target generation.
- Separate weather and air-quality data providers.
- Multiple model families.
- Time-series forecasting at 24, 48, and 72 hours.
- Chronological model evaluation.
- MLflow experiment tracking and registry.
- SHAP-based explainability.
- Automated repository workflows.
- Docker-based packaging.
- Cloud Run deployment.
- A documented EDA process.
- A reproducible first-run procedure.
- Security guidance for secrets and generated artifacts.
