VERSION=v5
DOCKERUSER=powerryan

build:
	docker build -f Dockerfile -t sentiment-rest .

push:
	docker tag sentiment-rest $(DOCKERUSER)/sentiment-rest:$(VERSION)
	docker push $(DOCKERUSER)/sentiment-rest:$(VERSION)
	docker tag sentiment-rest $(DOCKERUSER)/sentiment-rest:latest
	docker push $(DOCKERUSER)/sentiment-rest:latest
