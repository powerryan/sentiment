FROM python:3.6-slim

RUN    pip3 install pika

WORKDIR /srv
COPY    logs.py /srv
CMD    [ "python3", "logs.py"]
