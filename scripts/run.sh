#!/usr/bin/env sh

alembic upgrade head
uvicorn api.main:app --workers 4 --port 8080
