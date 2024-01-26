FROM python:3.11
RUN apt update && apt install -y postgresql
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
ENTRYPOINT ./run-migrations.sh
