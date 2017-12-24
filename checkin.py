#!/usr/bin/env python
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
from geopy import geocoders
from math import trunc
from tzlocal import get_localzone
import pytz
import requests
import sys
import time

API_KEY = 'l7xxb3dcccc4a5674bada48fc6fcf0946bc8'
USER_EXPERIENCE_KEY = 'AAAA3198-4545-46F4-9A05-BB3E868BEFF5'
BASE_URL = 'https://mobile.southwest.com/api/'

# Pulled from proxying the Southwest iOS App
headers = {'Host': 'mobile.southwest.com', 'Content-Type': 'application/json', 'X-API-Key': API_KEY, 'X-User-Experience-Id': USER_EXPERIENCE_KEY, 'Accept': '*/*'}

reservation_number = sys.argv[1]
first_name = sys.argv[2]
last_name = sys.argv[3]
checkin_early_seconds = 5
checkin_interval_seconds = 0.25
max_attemps = 40

def lookup_existing_reservation(number, first, last):
    # Find our existing record
    url = "{}mobile-misc/v1/mobile-misc/page/view-reservation/{}?first-name={}&last-name={}".format(BASE_URL, reservation_number, first_name, last_name)
    r = requests.get(url, headers=headers)
    return r.json()['viewReservationViewPage']

def get_checkin_data(number, first, last):
    url = "{}mobile-air-operations/v1/mobile-air-operations/page/check-in/{}?first-name={}&last-name={}".format(BASE_URL, reservation_number, first_name, last_name)
    r = requests.get(url, headers=headers)
    # if there is an error, die here
    if 'httpStatusCode' in body and body['httpStatusCode'] in ['NOT_FOUND', 'BAD_REQUEST']:
        print(body['message'])
        sys.exit()
    return r.json()

# work work work
body = lookup_existing_reservation(reservation_number, first_name, last_name)

# setup a geocoder
g = geocoders.GoogleV3()

# Get our local time
now = datetime.now(pytz.utc).astimezone(get_localzone())
tomorrow = now + timedelta(days=1)
date = now

# find the next departure time
for leg in body['bounds']:
    # calculate departure for this leg
    airport = "{}, {}".format(leg['departureAirport']['name'], leg['departureAirport']['state'])
    takeoff = "{} {}".format(leg['departureDate'], leg['departureTime'])
    date = datetime.strptime(takeoff, '%Y-%m-%d %H:%M').replace(tzinfo=g.timezone(g.geocode(airport).point))
    if date > now:
        break

# print found information
print("Flight information found, departing {} at {}".format(airport, date.strftime('%b %d %I:%M%p')))

# if we're outside of 24-hours before the flight, wait
if date > tomorrow:
    delta = (date-tomorrow).total_seconds() - checkin_early_seconds
    m, s = divmod(delta, 60)
    h, m = divmod(m, 60)
    print("Too early to check in.  Waiting {} hours, {} minutes, {} seconds".format(trunc(h), trunc(m), s))
    time.sleep(delta)

# get checkin data from first api call
data = get_checkin_data(reservation_number, first_name, last_name)
info_needed = data['checkInViewReservationPage']['_links']['checkIn']
url = "{}mobile-air-operations{}".format(BASE_URL, info_needed['href'])

success = False 
attempts = 0

while not success:
    print("Attempting check-in...")
    r = requests.post(url, headers=headers, json=info_needed['body'])
    body = r.json()

    if 'httpStatusCode' in body and body['httpStatusCode'] == 'FORBIDDEN':
        attempts += 1
        print(body['message'])
        if attempts > max_attemps:
            print("Max number of attempts exceeded, killing self")
            success = True
        else:
            print("Attempt {}, waiting {} seconds before retrying...".format(attempts, checkin_interval_seconds))
            time.sleep(checkin_interval_seconds)
    else:
        # Spit out info about boarding number
        for flight in body['checkInConfirmationPage']['flights']:
            for doc in flight['passengers']:
                print("{} got {}{}!".format(doc['name'], doc['boardingGroup'], doc['boardingPosition']))
        success = True
