FROM python:3.11

RUN set -ex \
    && curl https://pyenv.run | bash

RUN pip install pipenv

WORKDIR /app/migrations
COPY migrations/Pipfile migrations/Pipfile.lock /app/migrations
RUN PIPENV_VENV_IN_PROJECT=1 pipenv run pipenv install
WORKDIR /app
COPY . /app
ENV PATH="${PATH}:/app/migrations/.venv/bin/" 
CMD alembic upgrade head
