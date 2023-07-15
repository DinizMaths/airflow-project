# Algorithms and Data Structures

## Introduction

This project aims to apply the concept of pipelines. A pipeline is a sequence of interconnected steps that are executed in order to process data or perform specific tasks. In the context of this project, the goal is to create a pipeline using Apache Airflow.

Apache Airflow is a workflow and scheduling platform that allows you to create, schedule, and monitor complex workflows. 

By using Airflow, you can create a Directed Acyclic Graph (DAG) to represent the desired pipeline.

## aaa

```bash
virtualenv venv
```

Enter
```bash
source venv/bin/activate
```

download airflow
```bash
pip install apache-airflow
```

```bash
airflow db init
```

```bash
airflow users create --username <username> --firstname <seu nome> --lastname <seu sobrenome> --role Admin --email <seu email>
```

2 terminals 
```bash
airflow webserver
```

```bash
airflow scheduler
```