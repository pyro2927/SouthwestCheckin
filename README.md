# SW Checkin

![](http://www.southwest-heart.com/img/heart/heart_1.jpg)

This python script checks your flight reservation with Southwest and then checks you in at exactly 24 hours before your flight.  Queue up the script and it will `sleep` until the earliest possible check-in time.

## Requirements

This script can either be ran directly on your host or within Docker.

### Host

* Python (should work with 2.x or 3.x thanks to @ratabora)
* [pip](https://pypi.python.org/pypi/pip)

### Docker

* Docker (tested with 1.12.6)

## Setup

### Host

#### Install Base Package Requirements

```bash
$ pip install -r requirements.txt
```

#### Usage

```bash
$ python ./checkin.py CONFIRMATION_NUMBER FIRST_NAME LAST_NAME
```

### Docker

#### Usage

```bash
$ sudo docker build -t swcheckin ./
$ sudo docker run -ti swcheckin /tmp/checkin.py CONFIRMATION_NUMBER FIRST_NAME LAST_NAME
```
