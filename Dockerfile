FROM python:3.10-alpine

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip  \
    && pip install pip-tools  \
    && pip-sync requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host=0.0.0.0", "--port=80"]
