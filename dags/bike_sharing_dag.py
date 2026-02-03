from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os


sys.path.append('/opt/airflow/src')


from ingestion import load_data

from train import train_model     

default_args = {
    'owner': 'rama',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'bike_sharing_pipeline_v1',
    default_args=default_args,
    description='MLOps Pipeline for Bike Sharing Prediction',
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

    ingest_task >> train_task