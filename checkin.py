#!/usr/bin/env python
import requests
import sys
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta
import pytz
from tzlocal import get_localzone
import time

# Pulled from proxying the Southwest iOS App
headers = {'Host': 'mobile.southwest.com', 'Content-Type': 'application/vnd.swacorp.com.mobile.reservations-v1.0+json', 'X-API-Key': 'l7xxab4b3533b8d54bad9df230deb96a6f90', 'Accept': '*/*'}

reservation_number = sys.argv[1]
first_name = sys.argv[2]
last_name = sys.argv[3]

# Find our existing record
url = "https://mobile.southwest.com/api/extensions/v1/mobile/reservations/record-locator/{}?first-name={}&last-name={}".format(reservation_number, first_name, last_name)

r = requests.get(url, headers=headers)
body = r.json()

departure_time = body['itinerary']['originationDestinations'][0]['segments'][0]['departureDateTime']

date = parse(departure_time)
tomorrow = datetime.now(pytz.utc).astimezone(get_localzone()) + timedelta(days=1)

# Wait until checkin time
if date > tomorrow:
    delta = (date-tomorrow).total_seconds()
    print "Too early to check in, waiting {} seconds".format(delta)
    time.sleep(delta)

print "Attempting check-in..."

# Get our passengers to get boarding passes for
passengers = []
for passenger in body['passengers']:
    passengers.append({'firstName': passenger['secureFlightName']['firstName'], 'lastName': passenger['secureFlightName']['lastName']})

# Check in
headers['Content-Type'] = 'application/vnd.swacorp.com.mobile.boarding-passes-v1.0+json'
url = "https://mobile.southwest.com/api/extensions/v1/mobile/reservations/record-locator/{}/boarding-passes".format(reservation_number)
r = requests.post(url, headers=headers, json={'names': passengers})

body = r.json()

if 'httpStatusCode' in body and body['httpStatusCode'] == 'FORBIDDEN':
    print body['message']
else:
    # Spit out info about boarding number
    for checkinDocument in body['passengerCheckInDocuments']:
        for doc in checkinDocument['checkinDocuments']:
            print "You got {}{}!".format(doc['boardingGroup'], doc['boardingGroupNumber'])