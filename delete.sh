#!/bin/sh

kubectl delete deployment rabbitmq
kubectl delete deployment logs
kubectl delete deployment redis
kubectl delete deployment rest-server
kubectl delete deployment worker-server
kubectl delete service redis
kubectl delete service rabbitmq
kubectl delete service rest-server