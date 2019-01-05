#!/usr/bin/env python
"""Southwest Checkin.

Usage:
  checkin.py CONFIRMATION_NUMBER FIRST_NAME LAST_NAME [--email=<email_addr> | --mobile=<phone_num>] [-v | --verbose]
  checkin.py (-h | --help)
  checkin.py --version

Options:
  -h --help     Show this screen.
  -v --verbose  Show debugging information.
  --email=<email_addr>  Email address where notification will be sent to.
  --mobile=<phone_num>  Phone number where text notification will be sent to.
  --version     Show version.

"""
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
from docopt import docopt
from math import trunc
from tzlocal import get_localzone
import pytz
import requests
import sys
import time
import json

API_KEY = 'l7xxb3dcccc4a5674bada48fc6fcf0946bc8'
USER_EXPERIENCE_KEY = 'AAAA3198-4545-46F4-9A05-BB3E868BEFF5'
BASE_URL = 'https://mobile.southwest.com/api/'
CHECKIN_EARLY_SECONDS = 5
CHECKIN_INTERVAL_SECONDS = 0.25
MAX_ATTEMPTS = 40

# Pulled from proxying the Southwest iOS App
headers = {'Host': 'mobile.southwest.com', 'Content-Type': 'application/json', 'X-API-Key': API_KEY, 'X-User-Experience-Id': USER_EXPERIENCE_KEY, 'Accept': '*/*'}

# You might ask yourself, "Why the hell does this exist?"
# Basically, there sometimes appears a "hiccup" in Southwest where things
# aren't exactly available 24-hours before, so we try a few times
def safe_request(url, body=None):
    try:
        attempts = 0
        while True:
            if body is not None:
                r = requests.post(url, headers=headers, json=body)
            else:
                r = requests.get(url, headers=headers)
            data = r.json()
            if 'httpStatusCode' in data and data['httpStatusCode'] in ['NOT_FOUND', 'BAD_REQUEST', 'FORBIDDEN']:
                attempts += 1
                print(data['message'])
                if attempts > MAX_ATTEMPTS:
                    sys.exit("Unable to get data, killing self")
                time.sleep(CHECKIN_INTERVAL_SECONDS)
                continue
            return data
    except ValueError:
        # Ignore responses with no json data in body
        pass

def lookup_existing_reservation(number, first, last):
    # Find our existing record
    url = "{}mobile-misc/v1/mobile-misc/page/view-reservation/{}?first-name={}&last-name={}".format(BASE_URL, number, first, last)
    data = safe_request(url)
    return data['viewReservationViewPage']

def get_checkin_data(number, first, last):
    url = "{}mobile-air-operations/v1/mobile-air-operations/page/check-in/{}?first-name={}&last-name={}".format(BASE_URL, number, first, last)
    data = safe_request(url)
    return data['checkInViewReservationPage']

def checkin(number, first, last):
    data = get_checkin_data(number, first, last)
    info_needed = data['_links']['checkIn']
    url = "{}mobile-air-operations{}".format(BASE_URL, info_needed['href'])
    print("Attempting check-in...")
    return safe_request(url, info_needed['body'])['checkInConfirmationPage']

def send_notification(checkindata, emailaddr=None, mobilenum=None):
    info_needed = checkindata['_links']['boardingPasses']
    url = "{}mobile-air-operations{}".format(BASE_URL, info_needed['href'])
    mbpdata = safe_request(url, info_needed['body'])
    info_needed = mbpdata['checkInViewBoardingPassPage']['_links']
    url = "{}mobile-air-operations{}".format(BASE_URL, info_needed['href'])
    if emailaddr:
        info_needed['body']['mediaType'] = 'EMAIL'
        info_needed['body']['emailAddress'] = emailaddr
    if mobilenum:
        info_needed['body']['mediaType'] = 'SMS'
        info_needed['body']['phoneNumber'] = mobilenum
    print("Attempting to send boarding pass...")
    safe_request(url, info_needed['body'])

def schedule_checkin(flight_time, number, first, last, email, mobile):
    checkin_time = flight_time - timedelta(days=1)
    current_time = datetime.now(pytz.utc).astimezone(get_localzone())
    # check to see if we need to sleep until 24 hours before flight
    if checkin_time > current_time:
        # calculate duration to sleep
        delta = (checkin_time - current_time).total_seconds() - CHECKIN_EARLY_SECONDS
        # pretty print our wait time
        m, s = divmod(delta, 60)
        h, m = divmod(m, 60)
        print("Too early to check in.  Waiting {} hours, {} minutes, {} seconds".format(trunc(h), trunc(m), s))
        time.sleep(delta)
    data = checkin(number, first, last)
    for flight in data['flights']:
        for doc in flight['passengers']:
            print("{} got {}{}!".format(doc['name'], doc['boardingGroup'], doc['boardingPosition']))
    if email:
        send_notification(data, emailaddr=email)
    elif mobile:
        send_notification(data, mobilenum=mobile)


def auto_checkin(reservation_number, first_name, last_name, email=None, mobile=None):
    body = lookup_existing_reservation(reservation_number, first_name, last_name)

    # Get our local current time
    now = datetime.now(pytz.utc).astimezone(get_localzone())
    tomorrow = now + timedelta(days=1)

    # find all eligible legs for checkin
    for leg in body['bounds']:
        # calculate departure for this leg
        airport = "{}, {}".format(leg['departureAirport']['name'], leg['departureAirport']['state'])
        takeoff = "{} {}".format(leg['departureDate'], leg['departureTime'])
        tzrequest = {'iata': leg['departureAirport']['code'],
                     'country': 'ALL',
                     'db': 'airports',
                     'iatafilter': 'true',
                     'action': 'SEARCH',
                     'offset': '0'}
        tzresult = requests.post("https://openflights.org/php/apsearch.php", tzrequest)
        airport_tz = pytz.timezone(json.loads(tzresult.text)['airports'][0]['tz_id'])
        date = airport_tz.localize(datetime.strptime(takeoff, '%Y-%m-%d %H:%M'))
        if date > now:
            # found a flight for checkin!
            print("Flight information found, departing {} at {}".format(airport, date.strftime('%b %d %I:%M%p')))
            schedule_checkin(date, reservation_number, first_name, last_name, email, mobile)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Southwest Checkin 0.2')

    # work work
    reservation_number = arguments['CONFIRMATION_NUMBER']
    first_name = arguments['FIRST_NAME']
    last_name = arguments['LAST_NAME']
    email = arguments['--email']
    mobile = arguments['--mobile']

    auto_checkin(reservation_number, first_name, last_name, email, mobile)
