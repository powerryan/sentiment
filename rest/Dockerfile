FROM python:3.9

RUN    pip3 install flask flask-wtf redis Flask-Debug pika requests

RUN    mkdir /app
WORKDIR /app
COPY	. /app

EXPOSE	5000

CMD    python3 rest-server.py
