from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

import wikipedia

def install_libraries(**kwargs):
  pass


default_args = {
  "start_date": datetime(2023, 1, 1),
}

with DAG(dag_id="main_dag", description="This is the main DAG", default_args=default_args) as dag:
  task1 = BashOperator(task_id="tsk1", bash_command="pip install networkx")

  import wikipedia