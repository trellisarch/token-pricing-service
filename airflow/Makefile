.PHONY: shell install test

shell:
	pipenv shell

lint:
	pip install black
	black .

local-setup:
	
	cd .. && docker build -t migrations database -f database/Dockerfile
	cd .. && docker build -t local-airflow airflow -f airflow/Dockerfile
	cd .. && docker compose  -f airflow/docker-compose.yml up

local-test:
	pip install pipenv
	pipenv install -r requirements.txt
	pipenv install -r requirements-ci.txt
	pipenv run pytest
ci-test:
	pip install -r requirements.txt
	pip install -r requirements-ci.txt
	pytest