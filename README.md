🚴 Bike Sharing MLOps - Production Grade Pipeline
This is a comprehensive End-to-End MLOps project designed to predict bike-sharing demand. It integrates automated training, continuous monitoring, and real-time serving with a robust orchestration layer.
🚀 Project Overview
This project implements a complete machine learning lifecycle including:


ML Pipeline: Automated ingestion, validation, training, and testing.
+1


Orchestration: Apache Airflow for managing complex workflows.
+1


Tracking & Registry: MLflow for experiment management and model versioning.
+1


Monitoring: Evidently AI for data drift and Prometheus/Grafana for real-time metrics.
+1


API & UI: FastAPI for high-performance serving and Streamlit for an interactive dashboard.

🏗️ Architecture Flow
The system is built on a containerized microservices architecture:


Frontend (Port 8501): Streamlit app for user interaction.
+1


Backend API (Port 9999): FastAPI serving model predictions.
+1


Database: PostgreSQL for storing Airflow metadata and prediction logs.
+1


Storage: LocalStack simulating AWS S3 for monitoring reports.
+1


Monitoring: Prometheus (Scraping metrics) and Grafana (Visualization).
+1

🛠️ Tech Stack

Core: Python 3.9 


ML: Scikit-Learn (RandomForestRegressor) 
+2


Orchestration: Apache Airflow 


Tracking: MLflow 


Monitoring: Evidently AI, Prometheus, Grafana 


Infrastructure: Docker, Docker Compose, LocalStack 

🔄 The MLOps Lifecycle
1. Automated ML Pipeline (bike_sharing_final_pipeline_v4)
Runs daily to ensure the model is always fresh:


Ingestion & Validation: Checks data quality and schema.


Training: Trains a Random Forest model, logs metrics to MLflow, and saves the "Champion" model.
+1


E2E Testing: Calls the live API via host.docker.internal to verify serving readiness.
+1

2. Intelligent Monitoring & Retraining (model_monitoring_dag)

Drift Detection: Evidently AI compares current prediction data against training data.
+1


Short-Circuit Logic: If drift is NOT detected, the pipeline stops to save resources.


Auto-Retraining: If drift exceeds thresholds, an alert is sent to Slack, and a retraining job is automatically triggered.
+1

🖥️ Getting Started
Prerequisites
Docker Desktop

Python 3.9+

Git

Setup Instructions
Clone the repo:

Bash
git clone <your-repo-url>
cd bike-sharing-mlops
Start all services:

Bash
docker-compose up -d
Run the API on your Host machine (Windows):

Bash
pip install -r src/requirements.txt
python src/api.py
Access Ports

Airflow: http://localhost:8081 (admin/admin) 


MLflow: http://localhost:5000 


Streamlit: http://localhost:8501 


Grafana: http://localhost:3000 

📊 Monitoring Dashboard
The Grafana dashboard provides real-time insights into:

API Health: Status of the FastAPI service.

Total Predictions: Real-time counter of bike demand requests.

Latency: Average response time for the /predict endpoint.

System Metrics: Memory and CPU usage of the API.

📂 Project Structure
Plaintext
├── dags/             # Airflow DAG definitions
├── data/             # Raw and processed data (ignored by Git)
├── models/           # Trained .pkl models (ignored by Git)
├── src/              # Core source code (API, Training, Monitoring)
├── docker-compose.yml# Service orchestration
└── prometheus.yml    # Monitoring configuration
