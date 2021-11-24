#
# Worker server
#
import pickle
import platform
import io
import os
import sys
import pika
import redis
import hashlib
import json
import requests

from flair.models import TextClassifier
from flair.data import Sentence


hostname = platform.node()

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
classifier = TextClassifier.load('sentiment')
print(f"Connecting to rabbitmq({rabbitMQHost}) and redis({redisHost})")

##
## Set up redis connections
##
db_sentiment = redis.Redis(host=redisHost, db=1)                                                                           
db_sentence = redis.Redis(host=redisHost, db=2) 
##
## Set up rabbitmq connection
##
rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

rabbitMQChannel.queue_declare(queue='toWorker', durable=True)
rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
infoKey = f"{platform.node()}.worker.info"
debugKey = f"{platform.node()}.worker.debug"
def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)
def log_info(message, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)


##
## Your code goes here...
##
def callback(ch, method, properties, body):
    data = json.loads(body)
    model = data['model']
    sentences = data['sentences']
    res=[]
    for x in sentences:
        sentence = Sentence(x)
        classifier.predict(sentence)
        sentence = sentence.to_dict()
        res.append(sentence)
    for x in res:
        db_sentiment.sadd(model, json.dumps(x))

rabbitMQChannel.basic_qos(prefetch_count=1)
rabbitMQChannel.basic_consume(queue='toWorker', on_message_callback=callback)
print('Waiting for messages')
rabbitMQChannel.start_consuming()