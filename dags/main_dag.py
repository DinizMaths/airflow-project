from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator   import BashOperator
from airflow.utils.task_group          import TaskGroup
from datetime import datetime, timedelta


SEARCH_ARTICLE = "Graph neural network"
LIBREARIES = [
  "networkx",
  "matplotlib",
  "scipy",
  "seaborn",
  "wikipedia"
]
STOPS = (
  "International Standard Serial Number",
  "International Standard Book Number",
  "National Diet Library",
  "International Standard Name Identifier",
  "International Standard Book Number (Identifier)",
  "Pubmed Identifier",
  "Pubmed Central",
  "Digital Object Identifier",
  "Arxiv",
  "Proc Natl Acad Sci Usa",
  "Bibcode",
  "Library Of Congress Control Number",
  "Jstor",
  "Doi (Identifier)",
  "Isbn (Identifier)",
  "Pmid (Identifier)",
  "Arxiv (Identifier)",
  "Bibcode (Identifier)",
  "S2Cid (Identifier)",
  "Issn (Identifier)"
)

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
  import wikipedia

  todo_lst = [(0, SEARCH_ARTICLE)]
  todo_set = set(SEARCH_ARTICLE)
  done_set = set()

  graph = nx.DiGraph()
  layer, page = todo_lst[0]

  while layer < 2:
    del todo_lst[0]

    done_set.add(page)

    try:
      wiki = wikipedia.page(page)
    except:
      layer, page = todo_lst[0]

      continue

    for link in wiki.links:
      link = link.title()

      if link not in STOPS and not link.startswith("List Of"):
        if link not in todo_set and link not in done_set:
          todo_lst.append((layer + 1, link))
          todo_set.add(link)

        graph.add_edge(page, link)
        
    layer, page = todo_lst[0]

  nx.write_adjlist(graph, f"data/{kwargs['filename']}")

# === PREPROCESSING ===
def remove_plural(**kwargs):
  import networkx as nx

  graph = nx.read_adjlist(f"data/{kwargs['read_filename']}")

  duplicates = [(node, node + "s") for node in graph if node + "s" in graph]

  for dup in duplicates:
    graph = nx.contracted_nodes(graph, *dup, self_loops=False)
  
  nx.write_adjlist(graph, f"data/{kwargs['write_filename']}")

def remove_hyphen(**kwargs):
  import networkx as nx

  graph = nx.read_adjlist(f"data/{kwargs['read_filename']}")

  duplicates = [(x, y) for x, y in [(node, node.replace("-", " ")) for node in graph] if x != y and y in graph]

  for dup in duplicates:
    graph = nx.contracted_nodes(graph, *dup, self_loops=False)

  nx.write_adjlist(graph, f"data/{kwargs['write_filename']}")

def remove_selfloop(**kwargs):
  import networkx as nx

  graph = nx.read_adjlist(f"data/{kwargs['read_filename']}")

  graph.remove_edges_from(nx.selfloop_edges(graph))

  nx.write_adjlist(graph, f"data/{kwargs['write_filename']}")

def set_contraction(**kwargs):
  import networkx as nx

  graph = nx.read_adjlist(f"data/{kwargs['read_filename']}")

  nx.set_node_attributes(graph, 0, "contraction")
  nx.set_edge_attributes(graph, 0, "contraction")

  nx.write_adjlist(graph, f"data/{kwargs['write_filename']}")

def filter_nodes_by_degree_percentage(**kwargs):
  import networkx as nx

  graph = nx.read_adjlist(f"data/{kwargs['read_filename']}")

  degrees        = dict(graph.degree())
  sorted_nodes   = sorted(degrees, key=lambda x: degrees[x], reverse=True)
  num_nodes      = int(len(graph) * (kwargs["percentage"] / 100))
  filtered_nodes = sorted_nodes[:num_nodes]
  graph          = graph.subgraph(filtered_nodes)
  
  nx.write_adjlist(graph, f"data/{kwargs['write_filename']}")

# === PLOT ===
def remove_nodes_with_zero_degree(**kwargs):
  import networkx as nx

  graph = nx.read_adjlist(f"data/{kwargs['read_filename']}")

  nodes_with_zero_degree = [node for node in graph.nodes() if graph.degree[node] == 0]
  graph.remove_nodes_from(nodes_with_zero_degree)

  nx.write_adjlist(graph, f"data/{kwargs['write_filename']}")

def all_together_figure(**kwargs):
  import networkx as nx
  import matplotlib.pyplot as plt

  graph = nx.read_adjlist(f"data/{kwargs['filename']}")

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

  graph = nx.read_adjlist(f"data/{kwargs['filename']}")

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

  graph = nx.read_adjlist(f"data/{kwargs['filename']}")

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
  import networkx as nx
  import matplotlib.pyplot as plt
  import seaborn as sns
  import pandas as pd

  graph = nx.read_adjlist(f"data/{kwargs['filename']}")

  bc = pd.Series(nx.betweenness_centrality(graph))
  dc = pd.Series(nx.degree_centrality(graph))
  ec = pd.Series(nx.eigenvector_centrality(graph))
  cc = pd.Series(nx.closeness_centrality(graph))

  df = pd.DataFrame.from_dict({
    "Betweenness": bc,
    "Degree":      dc,
    "EigenVector": ec,
    "Closeness":   cc
  })

  df.reset_index(inplace=True, drop=True)

  fig = sns.PairGrid(df)

  fig.map_upper(sns.scatterplot)
  fig.map_lower(sns.kdeplot, cmap="Reds_r")
  fig.map_diag(sns.kdeplot, lw=2, legend=False)

  plt.savefig("figures/all.png", transparent=True, dpi=800, bbox_inches="tight")

def k_core_shell_figure(**kwargs):
  import matplotlib.patches as mpatches
  import networkx as nx
  import matplotlib.pyplot as plt
  import seaborn as sns

  graph = nx.read_adjlist(f"data/{kwargs['filename']}")
  
  fig, ax = plt.subplots(1, 1, figsize=(10, 8))

  graph_core_2 = nx.k_shell(graph, 2)
  graph_core_3 = nx.k_core(graph, 3)

  pos = nx.spring_layout(graph, seed=123426789, k=0.3)

  nx.draw_networkx_edges(graph, pos=pos, alpha=0.4, ax=ax)

  nodes = nx.draw_networkx_nodes(graph,        pos=pos, node_color="#333333")
  nodes = nx.draw_networkx_nodes(graph_core_2, pos=pos, node_color="blue")
  nodes = nx.draw_networkx_nodes(graph_core_3, pos=pos, node_color="red")

  red_patch  = mpatches.Patch(color='red',  label='3-core')
  blue_patch = mpatches.Patch(color='blue', label='5-shell')

  plt.legend(handles=[red_patch, blue_patch])

  plt.axis("off")
  plt.savefig("figures/k-core_sociopatterns.png", transparent=True, dpi=600)


with DAG(dag_id="main_dag", description="This is the main DAG", default_args=default_args) as dag:
  task1 = BashOperator(
    task_id="install_libraries", 
    bash_command=install_libraries_command(libraries=LIBREARIES)
  )

  task2 = PythonOperator(
    task_id="data_acquisition", 
    python_callable=data_acquisition, 
    op_kwargs={
      "filename": "raw_graph.adjlist"
    }
  )

  with TaskGroup("preprocessing") as group:
    with TaskGroup("remove_duplicates"):
      task3 = PythonOperator(
        task_id="remove_plural", 
        python_callable=remove_plural,  
        op_kwargs={
          "read_filename":  "raw_graph.adjlist", 
          "write_filename": "graph_wo_plural.adjlist"
        }
      )

      task4 = PythonOperator(
        task_id="remove_hyphen", 
        python_callable=remove_hyphen,  
        op_kwargs={
          "read_filename":  "graph_wo_plural.adjlist", 
          "write_filename": "graph_wo_plural_hyphen.adjlist"
        }
      )

      task5 = PythonOperator(
        task_id="remove_selfloop", 
        python_callable=remove_selfloop,  
        op_kwargs={
          "read_filename":  "graph_wo_plural_hyphen.adjlist", 
          "write_filename": "graph_wo_plural_hyphen_selfloop.adjlist"
        }
      )

    task6 = PythonOperator(
      task_id="set_contraction", 
      python_callable=set_contraction,  
      op_kwargs={
        "read_filename":  "graph_wo_plural_hyphen_selfloop.adjlist", 
        "write_filename": "graph_w_contraction_wo_plural_hyphen_selfloop.adjlist"
      }
    )

    task7 = PythonOperator(
      task_id="filter_nodes_by_degree_percentage", 
      python_callable=filter_nodes_by_degree_percentage,  
      op_kwargs={
        "read_filename":  "graph_w_contraction_wo_plural_hyphen_selfloop.adjlist", 
        "write_filename": "graph_filtered.adjlist",
        "percentage": 10
      }
    )

    task8 = PythonOperator(
      task_id="remove_nodes_with_zero_degree", 
      python_callable=remove_nodes_with_zero_degree,  
      op_kwargs={
        "read_filename":  "graph_filtered.adjlist", 
        "write_filename": "graph_preprocessed.adjlist"
      }
    )

  with TaskGroup("make_figures") as group:
    task9 = PythonOperator(
      task_id="plot_all_together", 
      python_callable=all_together_figure, 
      op_kwargs={
        "filename": "graph_preprocessed.adjlist"
      }
    )

    task10 = PythonOperator(
      task_id="plot_count_pdf", 
      python_callable=count_pdf_figure,
      op_kwargs={
        "filename": "graph_preprocessed.adjlist"
      }
    )

    task11 = PythonOperator(
      task_id="plot_count_cdf", 
      python_callable=count_cdf_figure,
      op_kwargs={
        "filename": "graph_preprocessed.adjlist"
      }
    )

    task12 = PythonOperator(
      task_id="plot_correlation", 
      python_callable=correlation_figure,
      op_kwargs={
        "filename": "graph_preprocessed.adjlist"
      }
    )

    task13 = PythonOperator(
      task_id="plot_k_core_shell", 
      python_callable=k_core_shell_figure,
      op_kwargs={
        "filename": "graph_preprocessed.adjlist"
      }
    )


  task1.set_downstream(task2)
  task2.set_downstream(task3)
  task3.set_downstream(task4)
  task4.set_downstream(task5)
  task5.set_downstream(task6)
  task6.set_downstream(task7)
  task7.set_downstream(task8)
  task8.set_downstream([task9, task10, task11, task12, task13])
