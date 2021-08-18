all: init test lint
init:
	pip install -e .[dev]

test:
	pytest --cov=southwest/ --cov=checkin

lint:
	pycodestyle */*.py --show-source --ignore=E501

docker:
	docker build -t pyro2927/southwestcheckin .

docker-test: docker
	docker run --rm -it pyro2927/southwestcheckin bash


release:
	docker push pyro2927/southwestcheckin

.PHONY: all
