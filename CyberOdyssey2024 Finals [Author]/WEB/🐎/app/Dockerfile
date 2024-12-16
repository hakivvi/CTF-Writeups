FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y default-mysql-client

RUN pip install --no-cache-dir Flask mysql-connector-python

EXPOSE 5000

CMD ["python", "app.py"]

