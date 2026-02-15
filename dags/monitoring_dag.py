from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from datetime import datetime
import pandas as pd
import json
import os
import sys
import requests
import boto3
from sqlalchemy import create_engine

# Path settings
sys.path.append('/opt/airflow')
try:
    from src.run_pipeline import run_pipeline
except ImportError:
    def run_pipeline():
        print("Pipeline import failed, but task is defined.")

# Evidently AI Imports
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.pipeline.column_mapping import ColumnMapping

# --- 1. S3 Helper Function (Bucket Auto-Creation) ---
def upload_to_s3(file_path, object_name):
    bucket_name = "monitoring-reports"
    s3_client = boto3.client(
        's3',
        endpoint_url='http://localstack:4566', 
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )
    try:
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except:
            print(f"📦 Creating bucket: {bucket_name}")
            s3_client.create_bucket(Bucket=bucket_name)

        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"✅ S3 Upload Success: {object_name}")
    except Exception as e:
        print(f"❌ S3 Upload Failed: {str(e)}")

# --- 2. Generate Monitoring Report ---
def generate_monitoring_report():
    try:
        engine = create_engine("postgresql://airflow:airflow@postgres/airflow")
        query = "SELECT * FROM predictions"
        df = pd.read_sql(query, engine)
        
        if len(df) < 5:
            print("❌ Not enough data for monitoring!")
            return False

        reference_df = df.sample(n=len(df)//2, random_state=42) 
        current_df = df.drop(reference_df.index)

        column_mapping = ColumnMapping()
       # column_mapping.target = 'raw_value'        
        column_mapping.prediction = 'predicted_cnt' 
        column_mapping.numerical_features = ['temp', 'atemp', 'hum', 'windspeed']
        column_mapping.categorical_features = ['season', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 'weathersit']
        monitoring_report = Report(metrics=[DataDriftPreset()])
        monitoring_report.run(
            reference_data=reference_df, 
            current_data=current_df, 
            column_mapping=column_mapping
        )
        
        report_path_json = "/opt/airflow/src/monitoring_report.json"
        report_path_html = "/opt/airflow/src/monitoring_report.html"
        
        monitoring_report.save_json(report_path_json)
        monitoring_report.save_html(report_path_html)
        
        report_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        upload_to_s3(report_path_html, f"bike_report_{report_ts}.html")
        print(f"✅ Report saved and shared: {report_path_html}")
        return True
    except Exception as e:
        print(f"❌ Error in report: {str(e)}")
        raise 

# --- 3. Smart Trigger (Check for Drift) ---
def check_for_issues(ti):
    report_path_json = "/opt/airflow/logs/monitoring_report.json"
    if not os.path.exists(report_path_json):
        return False
        
    try:
        with open(report_path_json, 'r') as f:
            data = json.load(f)
        
        drift_detected = False
        for metric in data.get('metrics', []):
            res = metric.get('result', {})
            if 'dataset_drift' in res:
                drift_detected = res['dataset_drift']

        # Statusని XComకి పంపుతున్నాం
        ti.xcom_push(key='drift_status', value="DETECTED 🚨" if drift_detected else "Normal ✅")
        
        # 🚨 డ్రిఫ్ట్ ఉంటేనే 'True' వెళ్తుంది, అప్పుడే స్లాక్ & రీ-ట్రైన్ రన్ అవుతాయి
        if drift_detected:
            print("🚨 Drift found! Triggering alerts and retraining.")
            return True
        else:
            print("✅ Everything is normal. Skipping retraining.")
            return False 
            
    except Exception as e:
        print(f"❌ Error in check: {str(e)}")
        return False

# --- 4. Slack Alert Function ---
def send_slack_manual(ti):
    webhook_url = os.getenv("SLACK_WEBHOOK")
    drift = ti.xcom_pull(task_ids='check_for_issues', key='drift_status')
    
    payload = {
        "text": (
            "🚨 *MLOps Alert: Action Required!* \n\n"
            f"• *Status:* {drift}\n"
            "• *Reason:* డేటాలో మార్పులు వచ్చాయి (Drift), అందుకే మోడల్‌ని *Retrain* చేస్తున్నాను! 🛠️"
        )
    }
    requests.post(webhook_url, json=payload, timeout=10)

# --- 5. DAG Definition ---
with DAG(
    dag_id='model_monitoring_dag',
    start_date=datetime(2026, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    monitor_task = PythonOperator(task_id='generate_report', python_callable=generate_monitoring_report)
    check_issues_task = ShortCircuitOperator(task_id='check_for_issues', python_callable=check_for_issues)
    send_slack_task = PythonOperator(task_id='send_slack_alert', python_callable=send_slack_manual)
    retrain_task = PythonOperator(task_id='retrain_model', python_callable=run_pipeline)

    # Workflow
    monitor_task >> check_issues_task >> [send_slack_task, retrain_task]