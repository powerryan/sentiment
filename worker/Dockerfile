FROM  dirkcgrunwald/flair:latest

RUN  pip3 install flask pika redis requests jsonpickle

WORKDIR /

COPY  worker-server.py /

#ENV    FLASK_PORT 5000

EXPOSE 5001

CMD python3 worker-server.py