# 🚴 Bike Sharing MLOps - Complete Flow Explanation

## 📊 System Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                         │
│                                                                   │
│  Browser → Streamlit UI (Port 8501) → FastAPI (Port 9999)       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PREDICTION FLOW                             │
│                                                                   │
│  1. User enters: temp, humidity, hour, season                    │
│  2. Streamlit sends HTTP GET to API                              │
│  3. API loads model (bike_model.pkl)                             │
│  4. Model predicts bike count                                    │
│  5. API saves prediction to PostgreSQL                           │
│  6. API returns result to Streamlit                              │
│  7. User sees predicted bike count                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ML PIPELINE FLOW (Airflow)                    │
│                                                                   │
│  DAG: bike_sharing_final_pipeline_v4 (Runs Daily)               │
│                                                                   │
│  Task 1: ingest_data                                             │
│    ↓ Check if data file exists                                   │
│    ↓ Verify file size                                            │
│                                                                   │
│  Task 2: validate_data                                           │
│    ↓ Check for required columns (cnt, temp)                      │
│    ↓ Check for null values                                       │
│    ↓ Fail pipeline if data is bad                                │
│                                                                   │
│  Task 3: train_model                                             │
│    ↓ Load processed data (X_train, y_train)                      │
│    ↓ Train RandomForest model                                    │
│    ↓ Log to MLflow (metrics, parameters)                         │
│    ↓ Register model in MLflow registry                           │
│    ↓ Set "champion" alias to latest version                      │
│    ↓ Save model locally (bike_model.pkl)                         │
│                                                                   │
│  Task 4: test_internal_prediction                                │
│    ↓ Load sample from training data                              │
│    ↓ Make prediction using saved model                           │
│    ↓ Verify model works inside Airflow                           │
│                                                                   │
│  Task 5: call_live_api_tracking                                  │
│    ↓ Call Windows API (host.docker.internal:9999)                │
│    ↓ Send test prediction request                                │
│    ↓ Verify API is serving predictions                           │
│    ↓ Check prediction is saved to database                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MONITORING FLOW (Airflow)                      │
│                                                                   │
│  DAG: model_monitoring_dag (Runs Daily)                          │
│                                                                   │
│  Task 1: generate_report                                         │
│    ↓ Load all predictions from PostgreSQL                        │
│    ↓ Split into reference vs current data                        │
│    ↓ Run Evidently AI drift detection                            │
│    ↓ Generate HTML + JSON reports                                │
│    ↓ Upload report to LocalStack S3                              │
│                                                                   │
│  Task 2: check_for_issues (ShortCircuit)                         │
│    ↓ Parse JSON report                                           │
│    ↓ Check if dataset_drift = True                               │
│    ↓ If NO drift → Stop pipeline (skip next tasks)               │
│    ↓ If DRIFT detected → Continue to alerts                      │
│                                                                   │
│  Task 3: send_slack_alert (Only if drift)                        │
│    ↓ Send message to Slack webhook                               │
│    ↓ Alert team about drift detection                            │
│                                                                   │
│  Task 4: retrain_model (Only if drift)                           │
│    ↓ Load fresh data                                             │
│    ↓ Train new model                                             │
│    ↓ Replace old model file                                      │
│    ↓ API automatically uses new model                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA FLOW                                   │
│                                                                   │
│  Raw Data (bike_sharing_raw.csv)                                 │
│    ↓                                                              │
│  Preprocessing (drop columns, split)                             │
│    ↓                                                              │
│  Processed Data (X_train, X_test, y_train, y_test)              │
│    ↓                                                              │
│  Training (RandomForest)                                         │
│    ↓                                                              │
│  Model File (bike_model.pkl)                                     │
│    ↓                                                              │
│  API loads model                                                 │
│    ↓                                                              │
│  Predictions saved to PostgreSQL                                 │
│    ↓                                                              │
│  Monitoring analyzes predictions                                 │
│    ↓                                                              │
│  Drift detected → Retrain                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete End-to-End Flow

### Step 1: Initial Setup
```
1. docker-compose up -d
   ↓ Starts 10 containers:
   - PostgreSQL (database)
   - LocalStack (S3 simulation)
   - Airflow (webserver + scheduler)
   - MLflow (experiment tracking)
   - Streamlit (frontend)
   - Prometheus (metrics)
   - Grafana (dashboards)

2. python src/api.py
   ↓ Starts FastAPI on Windows
   ↓ Connects to PostgreSQL
   ↓ Loads model file
   ↓ Ready to serve predictions
```

### Step 2: First-Time Training
```
Airflow UI → Trigger "bike_sharing_final_pipeline_v4"
   ↓
1. ingest_data: ✅ Data file found
   ↓
2. validate_data: ✅ Columns present, no nulls
   ↓
3. train_model:
   - Loads X_train.csv, y_train.csv
   - Trains RandomForest (100-200 trees)
   - RMSE calculated
   - Logged to MLflow
   - Model registered as version 1
   - Alias "champion" → version 1
   - Saved to models/bike_model.pkl
   ↓
4. test_internal_prediction: ✅ Model works
   ↓
5. call_live_api_tracking: ✅ API responds
```

### Step 3: Making Predictions
```
User opens Streamlit (localhost:8501)
   ↓
Adjusts sliders: temp=0.8, hr=18, season=2
   ↓
Clicks "Predict Bike Demand"
   ↓
Streamlit → GET http://host.docker.internal:9999/predict?temp=0.8&hr=18&season=2
   ↓
API receives request
   ↓
API loads bike_model.pkl
   ↓
Model predicts: 245 bikes
   ↓
API saves to PostgreSQL:
   INSERT INTO predictions (temp, hr, season, predicted_cnt, timestamp)
   ↓
API returns: {"predicted_bikes": 245}
   ↓
Streamlit displays: "Predicted Bikes Needed: 245"
   ↓
Balloons animation 🎈
```

### Step 4: Continuous Monitoring
```
Next day at midnight → monitoring_dag triggers
   ↓
1. generate_report:
   - SELECT * FROM predictions
   - Split: 50% reference, 50% current
   - Evidently compares distributions
   - Checks: temp, humidity, season, hour, etc.
   - Generates drift_report.html
   - Uploads to S3: bike_report_20260215_120000.html
   ↓
2. check_for_issues:
   - Reads drift_report.json
   - Checks: dataset_drift = True/False
   - If False → Pipeline stops ✅
   - If True → Continue ⚠️
   ↓
3. send_slack_alert (if drift):
   - POST to Slack webhook
   - Message: "🚨 Drift detected! Retraining..."
   ↓
4. retrain_model (if drift):
   - Loads fresh bike_sharing_raw.csv
   - Trains new RandomForest
   - Saves as bike_model.pkl (overwrites old)
   - API automatically uses new model
   - Next prediction uses updated model
```

### Step 5: Viewing Monitoring
```
User opens Streamlit
   ↓
Clicks "View Data Drift Report"
   ↓
Streamlit reads monitoring_report.html
   ↓
Displays embedded report:
   - Feature drift scores
   - Distribution comparisons
   - Statistical tests
   - Drift alerts
```

---

## 🎯 Key Flow Points

### 1. Docker Container Communication
```
Streamlit (container) → API (Windows host)
   Uses: host.docker.internal:9999
   Why: API runs on Windows, not in Docker

Airflow (container) → API (Windows host)
   Uses: host.docker.internal:9999
   Why: Same reason

API (Windows) → PostgreSQL (container)
   Uses: localhost:5432
   Why: PostgreSQL port mapped to host

Airflow (container) → MLflow (container)
   Uses: mlflow_server:5000
   Why: Both in same Docker network
```

### 2. Model Lifecycle
```
Training → MLflow Registry → Local File → API → Predictions
   ↓          ↓                ↓           ↓        ↓
Version 1   Tracked        bike_model   Serves   Logged
Version 2   Compared       .pkl file    Users    to DB
Version 3   Aliased        Updated      Fast     Monitored
```

### 3. Data Lifecycle
```
Raw CSV → Validation → Preprocessing → Training → Model
   ↓          ↓            ↓              ↓         ↓
17K rows   Checks      Split 80/20    RandomForest  PKL
Columns    Quality     X_train        Fit & Score   Saved
Features   Nulls       y_train        Metrics       Versioned
```

### 4. Monitoring Lifecycle
```
Predictions → Database → Drift Detection → Alert → Retrain
   ↓             ↓            ↓              ↓        ↓
Every API    PostgreSQL   Evidently AI   Slack    New Model
call         Logged       Compares       Notifies  Deployed
Timestamped  Queryable    Distributions  Team      Automatic
```

---

## 🔀 Decision Points in Flow

### 1. Data Validation
```
validate_data task:
   IF 'cnt' column missing → FAIL (stop pipeline)
   IF null values in 'cnt' → FAIL (stop pipeline)
   IF 'temp' column missing → FAIL (stop pipeline)
   ELSE → SUCCESS (continue to training)
```

### 2. Drift Detection
```
check_for_issues task:
   IF dataset_drift = False → STOP (skip alerts & retraining)
   IF dataset_drift = True → CONTINUE (alert & retrain)
```

### 3. Model Loading
```
API startup:
   IF bike_model.pkl exists → Load model
   IF bike_model.pkl missing → Return error 0.0
```

---

## ⚡ Performance Flow

### Request Latency
```
User clicks "Predict"
   ↓ 10ms - Streamlit processes
   ↓ 5ms - HTTP request to API
   ↓ 50ms - Model prediction
   ↓ 20ms - Database insert
   ↓ 5ms - HTTP response
   ↓ 10ms - Streamlit renders
Total: ~100ms
```

### Training Time
```
Full pipeline execution:
   ingest_data: 1 second
   validate_data: 2 seconds
   train_model: 30-60 seconds
   test_internal_prediction: 5 seconds
   call_live_api_tracking: 2 seconds
Total: ~1-2 minutes
```

### Monitoring Time
```
Monitoring DAG execution:
   generate_report: 10-30 seconds
   check_for_issues: 1 second
   send_slack_alert: 2 seconds
   retrain_model: 60 seconds (if triggered)
Total: 15-95 seconds (depending on drift)
```

---

## 🔄 Continuous Loop

```
Day 1:
   Train model → Deploy → Serve predictions → Log to DB

Day 2:
   Monitor predictions → No drift → Continue serving

Day 3:
   Monitor predictions → No drift → Continue serving

Day 7:
   Monitor predictions → DRIFT DETECTED!
   → Alert team
   → Retrain model
   → Deploy new model
   → Continue serving (with new model)

Day 8:
   Monitor predictions → No drift → Continue serving
   (cycle repeats)
```

---

## 📍 Where Each Component Fits

### Frontend Layer
- **Streamlit** (app.py): User interface
- **Browser**: User interaction point

### API Layer
- **FastAPI** (api.py): Prediction endpoint
- **Prometheus**: Metrics collection

### ML Layer
- **Training** (train.py): Model creation
- **Prediction** (predict.py): Inference logic
- **Evaluation** (evaluate.py): Performance metrics

### Data Layer
- **PostgreSQL**: Prediction storage
- **LocalStack S3**: Report storage
- **CSV Files**: Training data

### Orchestration Layer
- **Airflow**: Workflow automation
- **DAGs**: Pipeline definitions

### Monitoring Layer
- **Evidently AI**: Drift detection
- **Prometheus**: Metrics
- **Grafana**: Visualization
- **Slack**: Alerts

### Tracking Layer
- **MLflow**: Experiment tracking
- **Model Registry**: Version management

---

## 🎯 Summary: The Complete Flow

1. **User makes prediction** → Streamlit → API → Model → Database
2. **Airflow trains model** → Daily pipeline → MLflow → Model file
3. **Airflow monitors** → Daily check → Drift detection → Conditional retrain
4. **Prometheus tracks** → API metrics → Grafana dashboards
5. **Team gets alerts** → Slack notifications → Take action

**Everything is automated, monitored, and continuously improving!** 🚀
