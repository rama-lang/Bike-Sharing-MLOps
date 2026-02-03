from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hello():
    print("Hello Rama!")

with DAG('simple_test_dag', start_date=datetime(2026, 1, 1), schedule='@daily', catchup=False) as dag:
    t1 = PythonOperator(task_id='say_hello', python_callable=hello)