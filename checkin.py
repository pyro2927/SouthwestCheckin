#!/usr/bin/env python
"""Southwest Checkin.

Usage:
  checkin.py CONFIRMATION_NUMBER FIRST_NAME LAST_NAME [-v | --verbose]
  checkin.py RESERVATION_LIST [-v | --verbose]
  checkin.py (-h | --help)
  checkin.py --version

Options:
  -h --help     Show this screen.
  -v --verbose  Show debugging information.
  --version     Show version.

"""
from datetime import datetime, timedelta
from dateutil.parser import parse
from docopt import docopt
from math import trunc
from pytz import utc
from southwest import Reservation, openflights
from threading import Thread
import sys
import time

CHECKIN_EARLY_SECONDS = 5


def schedule_checkin(flight_time, reservation):
    checkin_time = flight_time - timedelta(days=1)
    current_time = datetime.utcnow().replace(tzinfo=utc)
    # check to see if we need to sleep until 24 hours before flight
    if checkin_time > current_time:
        # calculate duration to sleep
        delta = (checkin_time - current_time).total_seconds() - CHECKIN_EARLY_SECONDS
        # pretty print our wait time
        m, s = divmod(delta, 60)
        h, m = divmod(m, 60)
        print("Too early to check in.  Waiting {} hours, {} minutes, {} seconds".format(trunc(h), trunc(m), trunc(s)))
        try:
            time.sleep(delta)
        except OverflowError:
            print("System unable to sleep for that long, try checking in closer to your departure date")
            sys.exit(1)
    data = reservation.checkin()
    for flight in data['flights']:
        for doc in flight['passengers']:
            print("{} got {}{}!".format(doc['name'], doc['boardingGroup'], doc['boardingPosition']))


def auto_multi_checkin(reservation_details, verbose=False):
    details_list = reservation_details.split(',')
    num_reservations, r = divmod(len(details_list), 3)
    if r != 0:
        print("Incorrect number of details. Input should look like: \"AAAAAA,Jane,Smith,BBBBB,John,Smith\"")
        sys.exit()

    print("Starting check-in for the {} provided reservation{}".format(num_reservations, 's' if num_reservations != 1 else ''))
    threads = []

    # Create a list of 3-tuples containing the reservation details, i.e. [('AAAAA', 'Jane', 'Smith')]
    detail_tuples = list(zip(*[iter(details_list)]*3))
    for reservation in detail_tuples:
        t = Thread(target=auto_checkin, args=(reservation[0], reservation[1], reservation[2], verbose))
        t.daemon = True
        t.start()
        threads.append(t)

    handle_threads(threads)


def auto_checkin(reservation_number, first_name, last_name, verbose=False):
    r = Reservation(reservation_number, first_name, last_name, verbose)
    body = r.lookup_existing_reservation()

    # Get our local current time
    now = datetime.utcnow().replace(tzinfo=utc)
    tomorrow = now + timedelta(days=1)

    threads = []

    # find all eligible legs for checkin
    for leg in body['bounds']:
        # calculate departure for this leg
        airport = "{}, {}".format(leg['departureAirport']['name'], leg['departureAirport']['state'])
        takeoff = "{} {}".format(leg['departureDate'], leg['departureTime'])
        airport_tz = openflights.timezone_for_airport(leg['departureAirport']['code'])
        date = airport_tz.localize(datetime.strptime(takeoff, '%Y-%m-%d %H:%M'))
        if date > now:
            # found a flight for checkin!
            print("Flight information found for confirmation {}, departing {} at {}".format(reservation_number, airport, date.strftime('%b %d %I:%M%p')))
            # Checkin with a thread
            t = Thread(target=schedule_checkin, args=(date, r))
            t.daemon = True
            t.start()
            threads.append(t)

    handle_threads(threads)


def handle_threads(threads):
    # cleanup threads while handling Ctrl+C
    while True:
        if len(threads) == 0:
            break
        for t in threads:
            t.join(5)
            if not t.isAlive():
                threads.remove(t)
                break


if __name__ == '__main__':

    arguments = docopt(__doc__, version='Southwest Checkin 3')
    reservation_details = arguments['RESERVATION_LIST']
    reservation_number = arguments['CONFIRMATION_NUMBER']
    first_name = arguments['FIRST_NAME']
    last_name = arguments['LAST_NAME']
    verbose = arguments['--verbose']

    try:
        if reservation_number:
            auto_checkin(reservation_number, first_name, last_name, verbose)
        else:
            auto_multi_checkin(reservation_details, verbose)
    except KeyboardInterrupt:
        print("Ctrl+C detected, canceling checkin")
        sys.exit()
