from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
import os
import pandas as pd
import requests

# --- 1. API Call Function ---
def call_live_api_predict():
    # 🚨 Docker నుండి బయట ఉన్న Windows API ని పట్టుకోవడానికి ఇదే సరైన అడ్రస్
    API_URL = "http://host.docker.internal:9999/predict"
    
    # 🚨 'yr' తీసేశాను (మోడల్ కి ఇది తెలియదు కాబట్టి)
    params = {
        "season": 1, "mnth": 6, "hr": 10,
        "holiday": 0, "weekday": 3, "workingday": 1,
        "weathersit": 1, "temp": 0.5, "atemp": 0.5,
        "hum": 0.5, "windspeed": 0.1
    }
    
    print(f"🔗 Attempting to connect to: {API_URL}")
    try:
        # 15 సెకన్ల టైమ్ అవుట్ ఇచ్చాను
        response = requests.get(API_URL, params=params, timeout=60)
        
        if response.status_code == 200:
            print(f"✅ API SUCCESS! Prediction Saved: {response.json()}")
        else:
            print(f"❌ API Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"API failed with status {response.status_code}")
            
    except Exception as e:
        print(f"💥 Critical Connection Error: {str(e)}")
        # ఇక్కడ raise వాడటం వల్ల ఎర్రర్ వస్తే టాస్క్ Red అవుతుంది, అప్పుడు కారణం తెలుస్తుంది
        raise e

# --- 2. Internal Test Function ---
def run_inference_test():
    sys.path.append('/opt/airflow/src')
    from predict import make_prediction
    
    data_path = "/opt/airflow/data/processed/X_train.csv"
    if os.path.exists(data_path):
        sample_df = pd.read_csv(data_path).sample(n=1)
        # Feature mismatch రాకుండా 'yr' తీసేస్తున్నాం
        if 'yr' in sample_df.columns:
            sample_df = sample_df.drop(columns=['yr'])
        
        result = make_prediction(sample_df)
        print(f"✅ Internal Test Result: {result}")
    else:
        print("⚠️ Data path not found for internal test.")

# DAG Args
default_args = {
    'owner': 'rama',
    'retries': 0, # ఎర్రర్ వస్తే వెంటనే తెలియడానికి 0 పెట్టాను
    'retry_delay': timedelta(minutes=5),
}

# --- 3. DAG Definition (Named v4 to avoid Cache issues) ---
with DAG(
    'bike_sharing_final_pipeline_v4',
    default_args=default_args,
    description='Final Pipeline with host.docker.internal fix',
    schedule_interval='@daily', 
    start_date=days_ago(1),
    catchup=False
) as dag:

    ingest_task = BashOperator(
        task_id='ingest_data',
        bash_command='python /opt/airflow/src/ingestion.py'
    )

    validate_task = BashOperator(
        task_id='validate_data',
        bash_command='python /opt/airflow/src/validate_data.py'
    )

    train_task = BashOperator(
        task_id='train_model',
        bash_command='python /opt/airflow/src/train.py'
    )

    predict_task = PythonOperator(
        task_id='test_internal_prediction',
        python_callable=run_inference_test
    )

    api_task = PythonOperator(
        task_id='call_live_api_tracking',
        python_callable=call_live_api_predict
    )

    # Workflow
    ingest_task >> validate_task >> train_task >> predict_task >> api_task