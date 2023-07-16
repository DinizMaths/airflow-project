from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

DEPENDENCIES = [
  "networkx"
]

def install_libraries_command(**kwargs):
  libraries = kwargs["libraries"]

  libraries_string = ""

  for lib in libraries:
    libraries_string += lib + " "

  libraries_string = libraries_string.strip()
  
  return f"pip install {libraries_string}"

def read_graph(**kwargs):
  import networkx as nx

  g = nx.read_edgelist(f"data/{kwargs['file_name']}.txt", create_using=nx.Graph(), nodetype=int)


default_args = {
  "start_date": datetime(2023, 1, 1),
}

with DAG(dag_id="main_dag", description="This is the main DAG", default_args=default_args) as dag:
  task1 = BashOperator(
    task_id="install_libraries", 
    bash_command=install_libraries_command, 
    op_kwargs={
      "libraries": DEPENDENCIES
    }
  )

  task2 = PythonOperator(
    task_id="read_data", 
    python_callable=read_graph, 
    op_kwargs={
      "file_name": "facebook_combined"
    }
  )


  task1.set_downstream(task2)