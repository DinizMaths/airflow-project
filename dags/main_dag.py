from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator   import BashOperator
from airflow.utils.task_group          import TaskGroup
from datetime import datetime, timedelta

import json


DEPENDENCIES = [
  "networkx",
  "matplotlib",
  "scipy",
  "seaborn"
]

default_args = {
  "start_date": datetime(2023, 1, 1),
}


def install_libraries_command(**kwargs):
  libraries = kwargs["libraries"]

  libraries_string = ""

  for lib in libraries:
    libraries_string += lib + " "

  libraries_string = libraries_string.strip()
  
  return f"pip install {libraries_string}"

def data_acquisition(**kwargs):
  import networkx as nx

  graph = nx.Graph()

  graph.add_edges_from([
    ('a','d'),
    ('b','e'),
    ('c','e'),
    ('d','i'),
    ('e','i'),
    ('f','h'),
    ('g','h'),
    ('h','i'),('h','j'),
    ('i','l'),
    ('j','n'),
    ('l','m'),('l','n'),('l','k'),('l','o'),
    ('m','u'),
    ('n','k'),('n','o'),('n','s'),
    ('o','k'),('o','p'),('o','s'),
    ('p','k'),('p','s'),
    ('k','s'),('k','u'),
    ('q','s'),
    ('r','s'),
    ('s','u')
  ])

  nx.write_graphml(graph, f"data/{kwargs['file_name']}.graphml")

def preprocess_data(**kwargs):
  import networkx as nx

  graph = nx.read_graphml(f"data/{kwargs['read_file_name']}.graphml")

  for n, d in graph.nodes(data=True):
    graph.nodes[n]["class"] = graph.degree(n)

  nx.write_graphml(graph, f"data/{kwargs['write_file_name']}.graphml")

def all_together_figure(**kwargs):
  import networkx as nx
  import matplotlib.pyplot as plt

  graph = nx.read_graphml(f"data/{kwargs['file_name']}.graphml")

  fig, ax = plt.subplots(2, 2, figsize=(10, 8))

  max_centrality = max([
    max([v for k, v in nx.eigenvector_centrality(graph).items()]),
    max([v for k, v in nx.degree_centrality(graph).items()]),
    max([v for k, v in nx.closeness_centrality(graph).items()]),
    max([v for k, v in nx.betweenness_centrality(graph).items()])
  ])

  pos = nx.spring_layout(graph, seed=123456789, k=0.3)

  color_degree      = list(dict(nx.degree_centrality(graph)).values())
  color_closeness   = list(dict(nx.closeness_centrality(graph)).values())
  color_betweenness = list(dict(nx.betweenness_centrality(graph)).values())
  color_eigenvector = list(dict(nx.eigenvector_centrality(graph)).values())

  nx.draw_networkx_edges(graph, pos=pos, alpha=0.4, ax=ax[0,0])
  nx.draw_networkx_edges(graph, pos=pos, alpha=0.4, ax=ax[0,1])
  nx.draw_networkx_edges(graph, pos=pos, alpha=0.4, ax=ax[1,0])
  nx.draw_networkx_edges(graph, pos=pos, alpha=0.4, ax=ax[1,1])

  nodes = nx.draw_networkx_nodes(graph, pos=pos, node_color=color_degree,      cmap=plt.cm.jet, vmin=0, vmax=max_centrality, ax=ax[0,0])
  nodes = nx.draw_networkx_nodes(graph, pos=pos, node_color=color_closeness,   cmap=plt.cm.jet, vmin=0, vmax=max_centrality, ax=ax[0,1])
  nodes = nx.draw_networkx_nodes(graph, pos=pos, node_color=color_betweenness, cmap=plt.cm.jet, vmin=0, vmax=max_centrality, ax=ax[1,0])
  nodes = nx.draw_networkx_nodes(graph, pos=pos, node_color=color_eigenvector, cmap=plt.cm.jet, vmin=0, vmax=max_centrality, ax=ax[1,1])

  nx.draw_networkx_labels(graph, pos=pos, font_color='white', ax=ax[0,0])
  nx.draw_networkx_labels(graph, pos=pos, font_color='white', ax=ax[0,1])
  nx.draw_networkx_labels(graph, pos=pos, font_color='white', ax=ax[1,0])
  nx.draw_networkx_labels(graph, pos=pos, font_color='white', ax=ax[1,1])

  ax[0,0].axis("off")
  ax[1,0].axis("off")
  ax[0,1].axis("off")
  ax[1,1].axis("off")

  ax[0,0].set_title("Degree Centraliy")
  ax[0,1].set_title("Closeness Centraliy")
  ax[1,0].set_title("Betweenness Centraliy")
  ax[1,1].set_title("Eigenvector Centraliy")

  plt.subplots_adjust(bottom=0.0, right=0.92, top=1.0)

  cax  = plt.axes([0.95, 0.3, 0.025, 0.4])
  sm   = plt.cm.ScalarMappable(cmap=plt.cm.jet, norm=plt.Normalize(vmin=0, vmax=max_centrality))
  cbar = plt.colorbar(sm, cax)

  plt.savefig("figures/alltogether.png", transparent=True, dpi=600, bbox_inches="tight")

def count_pdf_figure(**kwargs):
  import networkx as nx
  import matplotlib.pyplot as plt
  import seaborn as sns

  graph = nx.read_graphml(f"data/{kwargs['file_name']}.graphml")

  degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)  

  plt.style.use("fivethirtyeight")

  fig, ax = plt.subplots(1, 1, figsize=(10, 8))

  sns.histplot(degree_sequence, bins=7, label="Count", ax=ax)
  ax2 = ax.twinx()
  sns.kdeplot(degree_sequence, color='r', label="Probability Density Function (PDF)", ax=ax2)

  # ask matplotlib for the plotted objects and their labels
  lines, labels = ax.get_legend_handles_labels()
  lines2, labels2 = ax2.get_legend_handles_labels()
  ax2.legend(lines + lines2, labels + labels2, loc=0)

  ax.grid(False)
  ax2.grid(False)
  ax.set_xlabel("Degree")
  ax2.set_ylabel("Probability")

  plt.savefig("figures/probability_density_function.png", transparent=True, dpi=600, bbox_inches="tight")

def count_cdf_figure(**kwargs):
  import networkx as nx
  import matplotlib.pyplot as plt
  import seaborn as sns

  graph = nx.read_graphml(f"data/{kwargs['file_name']}.graphml")

  degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)  

  plt.style.use("fivethirtyeight")

  fig, ax = plt.subplots(1, 1, figsize=(10, 8))

  sns.histplot(degree_sequence, bins=7, label="Count", ax=ax)
  ax2 = ax.twinx()
  sns.kdeplot(degree_sequence, color='r', label="Cumulative Density Function (CDF)", ax=ax2, cumulative=True)

  lines, labels   = ax.get_legend_handles_labels()
  lines2, labels2 = ax2.get_legend_handles_labels()

  ax2.legend(lines + lines2, labels + labels2, loc=0)

  ax.grid(False)
  ax2.grid(False)
  ax.set_xlabel("Degree")
  ax2.set_ylabel("Probability")

  plt.savefig("figures/cumulative_density_function.png", transparent=True, dpi=600, bbox_inches="tight")

def correlation_figure(**kwargs):
  pass

def k_core_shell_figure(**kwargs):
  pass


with DAG(dag_id="main_dag", description="This is the main DAG", default_args=default_args) as dag:
  task1 = BashOperator(task_id="install_libraries", bash_command=install_libraries_command(libraries=DEPENDENCIES))

  with TaskGroup("preprocessing") as group:
    task2 = PythonOperator(
      task_id="data_acquisition", 
      python_callable=data_acquisition, 
      op_kwargs={
        "file_name": "raw_graph"
      }
    )

    task3 = PythonOperator(
      task_id="preprocess_data", 
      python_callable=preprocess_data,  
      op_kwargs={
        "read_file_name": "raw_graph", 
        "write_file_name": "preprocessed_graph"
      }
    )

  with TaskGroup("make_figures") as group:
    task4 = PythonOperator(
      task_id="plot_all_together", 
      python_callable=all_together_figure, 
      op_kwargs={
        "file_name": "preprocessed_graph"
      }
    )

    task5 = PythonOperator(
      task_id="plot_count_pdf", 
      python_callable=count_pdf_figure,
      op_kwargs={
        "file_name": "preprocessed_graph"
      }
    )

    task6 = PythonOperator(
      task_id="plot_count_cdf", 
      python_callable=count_cdf_figure,
      op_kwargs={
        "file_name": "preprocessed_graph"
      }
    )

    task7 = PythonOperator(
      task_id="plot_correlation", 
      python_callable=correlation_figure,
      op_kwargs={
        "file_name": "preprocessed_graph"
      }
    )

    task8 = PythonOperator(
      task_id="plot_k_core_shell", 
      python_callable=k_core_shell_figure,
      op_kwargs={
        "file_name": "preprocessed_graph"
      }
    )


  task1.set_downstream(task2)
  task2.set_downstream(task3)
  task3.set_downstream([task4, task5, task6, task7, task8])
