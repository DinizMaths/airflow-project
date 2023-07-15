from airflow import DAG
from datetime import datetime, timedelta

default_args = {
  "owner": "me",
  "retry_delay": timedelta(minutes=2)
}

with DAG(dag_id="main_dag", description="This is the main DAG", start_date=datetime(2023, 1, 1), default_args=default_args) as dag:
  pass