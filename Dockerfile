FROM python:3.10-alpine

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip  \
    && pip install pip-tools  \
    && pip-sync requirements.txt

COPY . .

RUN chmod u+x ./scripts/run.sh

EXPOSE 80

CMD [ "./scripts/run.sh" ]