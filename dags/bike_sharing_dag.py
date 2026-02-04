from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago # <--- ఇది యాడ్ చేశాను
from datetime import datetime, timedelta
import sys
import os

# src ఫోల్డర్ పాత్
sys.path.append('/opt/airflow/src')

try:
    from ingestion import load_data
    from train import train_model 
except ImportError as e:
    print(f"Import Error: {e}")

# Inference Test Function
def run_inference_test():
    import pandas as pd
    from predict import make_prediction
    
    data_path = "/opt/airflow/data/processed/X_train.csv"
    
    if os.path.exists(data_path):
        full_df = pd.read_csv(data_path)
        sample_df = full_df.sample(n=1)
        
        # 'temp' ని మార్చుతున్నాం వాల్యూ మారుతుందో లేదో చూడటానికి
        if 'temp' in sample_df.columns:
            sample_df['temp'] = 0.9  
        
        print(f"🚀 Forced Input Data: {sample_df.iloc[0].to_dict()}")
        sample_df = sample_df.astype(float)
        
        result = make_prediction(sample_df)
        print(f"✅ Prediction Result: {result}")
    else:
        raise FileNotFoundError(f"Data missing at {data_path}")

default_args = {
    'owner': 'rama',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# --- ఒకే ఒక DAG డెఫినిషన్ ఉండాలి ---
with DAG(
    'bike_sharing_final_pipeline_v2',
    default_args=default_args,
    description='Automated 5-min Retraining Pipeline',
    schedule_interval='*/5 * * * *',  # ప్రతి 5 నిమిషాలకు ఒకసారి
    start_date=days_ago(0),           # వెంటనే స్టార్ట్ అవుతుంది
    catchup=False
) as dag:

    ingest_task = PythonOperator(
        task_id='ingest_data',
        python_callable=load_data
    )

    train_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model
    )

    predict_task = PythonOperator(
        task_id='test_prediction_tracking',
        python_callable=run_inference_test
    )

    # టాస్క్ ఆర్డర్
    ingest_task >> train_task >> predict_task