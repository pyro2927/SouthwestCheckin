# SW Checkin

![](http://www.southwest-heart.com/img/heart/heart_1.jpg)

This python script checks your flight reservation with Southwest and then checks you in at exactly 24 hours before your flight.  Queue up the script and it will `sleep` until the earliest possible check-in time.

## Requirements

* Python 2.x
* [pip](https://pypi.python.org/pypi/pip)

## Setup

```bash
$ pip install -r requirements.txt
```

## Usage

```bash
$ python ./checkin.py CONFIRMATION_NUMBER FIRST_NAME LAST_NAME
```
