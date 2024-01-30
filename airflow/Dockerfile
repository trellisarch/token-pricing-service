FROM apache/airflow:2.8.1

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./dags/ /opt/airflow/dags
USER airflow
