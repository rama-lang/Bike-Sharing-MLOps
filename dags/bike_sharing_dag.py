from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os
import pandas as pd

# src ఫోల్డర్ పాత్
sys.path.append('/opt/airflow/src')

try:
    from ingestion import load_data
    from train import train_model 
    from predict import make_prediction
except ImportError as e:
    print(f"Import Error: {e}")

def run_inference_test():
    import pandas as pd
    import os
    
    # డేటా పాత్ ఇక్కడ ఉండాలి
    data_path = "/opt/airflow/data/processed/X_train.csv"
    
    if os.path.exists(data_path):
        full_df = pd.read_csv(data_path)
        sample_df = full_df.sample(n=1)
        
        # 💥 మ్యాజిక్: 'temp' ని మార్చుతున్నాం వాల్యూ మారుతుందో లేదో చూడటానికి
        if 'temp' in sample_df.columns:
            sample_df['temp'] = 0.9  
        
        print(f"🚀 Forced Input Data: {sample_df.iloc[0].to_dict()}")
        
        sample_df = sample_df.astype(float)
        
        # Prediction logic
        from predict import make_prediction
        result = make_prediction(sample_df)
        print(f"✅ Prediction Result: {result}")
    else:
        raise FileNotFoundError(f"Data missing at {data_path}")

default_args = {
    'owner': 'rama',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'bike_sharing_final_pipeline_v2', # పేరు మార్చాం Fresh Start కోసం
    default_args=default_args,
    schedule_interval='@daily',
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

    ingest_task >> train_task >> predict_task