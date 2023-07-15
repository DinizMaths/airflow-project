# Algorithms and Data Structures

## Introduction

This project aims to apply the concept of pipelines. A pipeline is a sequence of interconnected steps that are executed in order to process data or perform specific tasks. In the context of this project, the goal is to create a pipeline using Apache Airflow.

Apache Airflow is a workflow and scheduling platform that allows you to create, schedule, and monitor complex workflows. 

By using Airflow, you can create a Directed Acyclic Graph (DAG) to represent the desired pipeline.

## TEST

At the directory of the project

```bash
curl -Lf0 https://airflow.apache.org/docs/apache-airflow/2.6.3/docker-compose.yaml
```


```bash
mkdir ./dags ./logs ./plugins
```

```bash
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
```

```bash
docker-compose up airflow-init
```

```bash
docker-compose up -d
```

```bash
Username: airflow
Password: airflow
```

AIRFLOW__CORE__LOAD_EXAMPLES: 'false'