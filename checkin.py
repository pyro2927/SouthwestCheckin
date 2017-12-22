#!/usr/bin/env python
import requests
import sys
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta
import pytz
from tzlocal import get_localzone
import time
from math import trunc

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
    return r.json()

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

# wait until we have the proper time
# TODO: get the fucking time
now = datetime.now(pytz.utc).astimezone(get_localzone())
tomorrow = now + timedelta(days=1)
date = now

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
