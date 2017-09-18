FROM python:3.6.2
COPY ./requirements.txt /tmp/
COPY ./checkin.py /tmp/
WORKDIR /tmp/
RUN pip install -r requirements.txt
