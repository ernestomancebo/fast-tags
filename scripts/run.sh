#!/usr/bin/env sh

alembic upgrade head
uvicorn api.main:app --workers 4 --host 0.0.0.0 --port 8080
