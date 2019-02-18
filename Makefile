init:
    pip install -r requirements.txt

test:
    pytest --cov=southwest/ --cov=checkin

.PHONY: init test
