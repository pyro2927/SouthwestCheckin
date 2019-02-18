all: init test lint
init:
	pip install -r requirements.txt

test:
	pytest --cov=southwest/ --cov=checkin

lint:
	pycodestyle */*.py --show-source --ignore=E501

.PHONY: all
