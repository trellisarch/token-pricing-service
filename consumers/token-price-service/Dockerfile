FROM python:3.10

WORKDIR /src
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app/ /app
WORKDIR /

ENTRYPOINT uvicorn app.main:app --workers 6 --host 0.0.0.0 --port 8000 --log-level info
