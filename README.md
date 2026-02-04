🚲 End-to-End MLOps: Bike-Sharing Demand PredictionThis repository demonstrates a production-ready Automated Machine Learning Pipeline. It covers the entire lifecycle from data ingestion to automated model promotion and CI/CD.

🏗️ Project ArchitectureThe pipeline is built on three main pillars:Orchestration (Airflow): Schedules and manages the workflow tasks.Model Governance (MLflow): Tracks experiments and manages the "Champion" model via the Model Registry.Infrastructure (Docker): Containerizes the entire stack, including LocalStack (S3) and the Airflow environment.

🚀 Key FeaturesContinuous Training (CT): Automated retraining triggers via Airflow to handle new data.Experiment Tracking: 
Logging hyperparameters (e.g., n_estimators) and performance metrics (RMSE) using MLflow.Model Registry: 
Automated versioning with the @champion alias for seamless production deployment.Cloud Simulation: Integrated LocalStack to simulate AWS S3 for data ingestion without cloud costs.CI/CD Pipeline: 
Automated code quality and syntax checks using GitHub Actions.

🛠️ Tech StackCategoryTechnologyLanguagePython 3.9+OrchestrationApache AirflowML Tracking & RegistryMLflowCloud SimulationLocalStack (AWS S3)ContainerizationDocker & Docker ComposeCI/CDGitHub Actions
📈 Pipeline WorkflowIngest: Fetches raw data from S3 (LocalStack) using boto3 and caches it in data/processed.Train: 
Trains a Scikit-learn Random Forest model with dynamic hyperparameter logging.Evaluate & Register: 
Compares new results with the existing @champion and registers the new version.Predict: 
Loads the current @champion from the Registry for real-time or batch inference.

💻 Setup & Run1. Start the InfrastructureSpin up the Airflow and MLflow containers:
PowerShelldocker-compose up -d

2. Setup LocalStack S3 (One-time)Simulate the cloud environment and upload the raw dataset:
PowerShell# Create the S3 Bucket
docker exec -it localstack_main awslocal s3 mb s3://bike-sharing-data

# Upload Raw Data to S3
docker cp data/raw/bike_sharing_raw.csv localstack_main:/tmp/data.csv
docker exec -it localstack_main awslocal s3 cp /tmp/data.csv s3://bike-sharing-data/bike_sharing_raw.csv
3. MonitoringAirflow UI: http://localhost:8080 (Check DAG status)MLflow UI: http://localhost:5000 (Compare model versions)

Folder Structure:
.
├── .github/
│   └── workflows/
│       └── main.yml            # GitHub Actions (CI/CD)
├── dags/
│   └── bike_sharing_dag.py     # Airflow DAG (The Heart)
├── src/
│   ├── ingestion.py            # S3 Data Pulling
│   ├── train.py                # Model Training & MLflow Registry
│   ├── predict.py              # Inference Logic (The Brain)
│   └── app.py                  # Streamlit/Flask UI
├── data/                       # Local Data Storage
├── docker-compose.yaml         # Container Orchestration
├── Dockerfile                  # Image Build Instructions
├── requirements.txt            # Python Dependencies
└── README.md                   # Project Documentation
