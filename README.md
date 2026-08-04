# Telecom Security System

An end-to-end proof-of-concept telecom security system that simulates network threat detection, trains supervised and unsupervised models, and exposes a live analytics dashboard.

## Project Overview

This repository demonstrates a telecom security operations workflow with:

- A synthetic dataset generator for telecom traffic and attack vectors
- A preprocessing pipeline that scales data and balances classes with SMOTE
- Dual AI engines: `RandomForestClassifier` for supervised fraud detection and `IsolationForest` for anomaly detection
- A FastAPI backend that scores incoming telecom events and exposes live simulation endpoints
- A Streamlit-based SOC dashboard for real-time monitoring, topology visualization, and dataset exploration
- A 3D network threat visualization exported as `3d_fraud_network.html`

## Key Features

- Synthetic dataset creation for telecom traffic and attack scenarios
- Data preprocessing, scaling, and class imbalance handling
- Supervised signature-based threat detection plus unsupervised anomaly discovery
- Real-time event simulation with risk scoring and severity alerts
- Backend API for prediction and simulation
- Streamlit UI with live feed, local topology, global origins, and dataset tabs

## Contents

- `data/telecom_security_data.csv` — Generated telecom traffic dataset
- `models/` — Saved machine learning artifacts
- `src/api.py` — FastAPI backend for threat inference and simulation
- `src/app.py` — Streamlit dashboard frontend
- `src/data_generator.py` — Synthetic telecom dataset generator
- `src/preprocessor.py` — Data preprocessing and scaler persistence
- `src/train_models.py` — Model training and evaluation script
- `src/real_time_engine.py` — Threat detection engine and live traffic simulator
- `src/threat_intelligence.py` — Advanced threat analysis and 3D visualization helper
- `3d_fraud_network.html` — Exported 3D network threat graph

## Requirements

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Setup and Usage

1. Generate or prepare the dataset:

```bash
python src/data_generator.py
```

2. Preprocess the dataset and save the scaler:

```bash
python src/preprocessor.py
```

3. Train the detection models:

```bash
python src/train_models.py
```

4. Start the FastAPI backend:

```bash
python src/api.py
```

5. Start the Streamlit dashboard:

```bash
streamlit run src/app.py
```

6. Open the Streamlit UI in your browser and verify the backend status in the sidebar.

## API Endpoints

- `GET /` — Health check
- `POST /api/v1/predict` — Score a telecom event payload
- `GET /api/v1/simulate` — Generate and score a live simulated event

## Example Predict Payload

```json
{
  "session_duration": 120.5,
  "packet_rate": 55.2,
  "login_attempts": 1,
  "location_switch_freq": 0,
  "bandwidth_usage": 4.5,
  "call_failures": 0
}
```

## Notes

- The backend loads models from `models/random_forest_engine.pkl`, `models/isolation_forest_engine.pkl`, and `models/scaler.pkl`.
- If the models are missing, run `src/preprocessor.py` and `src/train_models.py` first.
- The Streamlit dashboard reads the backend URL from the `API_URL` environment variable, defaulting to `http://127.0.0.1:8000`.

## License

This project was developed as a learning and demonstration tool for telecom security analytics. It is provided as-is with no warranty, and you are free to explore, modify, and adapt the code for your own experiments.
