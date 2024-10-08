# Image tag version must match airflowVersion in deploy/helm/airflow/helmfile.yaml
FROM apache/airflow:2.9.3

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./dags/ /opt/airflow/dags
USER airflow
