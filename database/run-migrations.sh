#!/bin/bash
set -e

python setup_db.py
alembic upgrade head
