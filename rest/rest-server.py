##
from flask import Flask, request, Response, jsonify
import platform
import io, os, sys
import redis
import pika
import requests
import json

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

## my code below

app = Flask(__name__)

db_sentiment = redis.Redis(host=redisHost, db=1)                                                                           
db_sentence = redis.Redis(host=redisHost, db=2)

def log(channel, routing_key, message):
    print(f"{routing_key}: {message}")
    err_log = channel.basic_publish(
        exchange='logs',
        routing_key=routing_key,
        body=message,
    )
    if (err_log):
        print("error: ", err_log)

def toWorker(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitMQHost))
    channel = connection.channel()
    channel.queue_declare(queue='toWorker', durable=True)
    channel.exchange_declare(exchange='logs', exchange_type='topic')
    channel.basic_publish(
            exchange='',
            routing_key = 'toWorker',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2))
    connection.close()

@app.route('/')
def hello():
    return '<h1>Sentiment App</h1><p>Hello</p>'

@app.route('/apiv1/analyze/', methods=['POST'])
def analyze():
    json_data = request.get_json()
    toWorker(json_data)  
    msg = {"action": "queued"}
    json_msg = json.dumps(msg)
    return Response(response = json_msg, status = 200, mimetype = "application/json")

@app.route('/apiv1/cache/<string:model>', methods=['GET'])
def cache(model):
    db_data = db_sentiment.smembers(model)
    res=[]
    for x in db_data:
        res.append(json.loads(x))
    json_data = json.dumps(res)
    return Response(response = json_data, status = 200, mimetype = "application/json")

#had wrong route - double check
@app.route('/apiv1/sentence', methods=['GET'])
def sentence():
    json_data = request.get_json()
    model = json_data['model']
    sentences = json_data['sentences']
    db_data = db_sentiment.smembers(model)
    db_data = [json.loads(i) for i in db_data]
    res=[]
    for s in sentences:
        for d in db_data:
            if d['text'] == s:
                res.append(d)
    
    print('sentence request from user', flush=True)
    jsonres = json.dumps(res)
    return Response(response = jsonres, status = 200, mimetype = "application/json")

app.run(host="0.0.0.0", port=5000,debug=False)
