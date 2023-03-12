#!/bin/bash
alembic upgrade head
uvircorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80