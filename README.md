🚲 Bike-Sharing Demand Prediction (End-to-End MLOps)
This project implements a production-ready Machine Learning pipeline to predict bike-sharing demand. It demonstrates core MLOps principles including data ingestion from simulated cloud storage, containerization, and automated API deployment.

🏗️ Project Architecture
The architecture follows a modular approach to ensure scalability and reproducibility:

Data Lake (S3): Raw data is hosted in a LocalStack S3 bucket to simulate AWS cloud environments.

Ingestion Layer: A Python-based ingestion script fetches data using boto3 and handles local caching.

Inference Service: A FastAPI application serves model predictions in real-time.

Orchestration: Entire stack is containerized using Docker with a custom bridge network for secure inter-container communication.

🚀 Getting Started
1. Prerequisites
Docker & Docker Desktop

Python 3.12+

AWS CLI (optional, for manual S3 checks)

2. Network & Infrastructure Setup
First, create a dedicated network so the app and LocalStack can communicate:

PowerShell
docker network create bike-mlops-net
Start LocalStack:

PowerShell
docker run --rm -d --name localstack_main --network bike-mlops-net -p 4566:4566 localstack/localstack
3. Data Preparation (S3 Simulation)
Create the bucket and upload the raw dataset:

PowerShell
# Create Bucket
docker exec -it localstack_main awslocal s3 mb s3://bike-sharing-data

# Upload Data
docker cp data/raw/bike_sharing_raw.csv localstack_main:/tmp/data.csv
docker exec -it localstack_main awslocal s3 cp /tmp/data.csv s3://bike-sharing-data/bike_sharing_raw.csv
4. Build and Launch the API
Build the Docker image and run the prediction service:

PowerShell
docker build -t bike-prediction-app .
docker run -p 8000:8000 --network bike-mlops-net bike-prediction-app
🧪 API Usage
Once the container is running, access the interactive API documentation at: 👉 http://localhost:8000/docs

Example Request:

Endpoint: /predict

Payload: Provide values for season, hr, temp, etc.

Response: {"predicted_bikes": 19} (Sample output)

🧠 Key MLOps Challenges Solved
Container Networking: Resolved [Errno -2] by implementing a custom Docker bridge network, allowing seamless communication between the app and LocalStack.

Cloud Simulation: Integrated LocalStack to test S3 ingestion logic without incurring AWS costs.

Configuration Management: Utilized config.yaml to decouple environment variables from the core logic, ensuring the pipeline is portable.
