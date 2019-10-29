import json
import pytest
import requests
import southwest
import checkin
from datetime import datetime, timedelta
from .my_vcr import custom_vcr
from pytz import timezone

my_vcr = custom_vcr()
r = southwest.Reservation('XXXXXX', 'John', 'Smith')


@my_vcr.use_cassette()
def test_generate_headers():
    headers = southwest.Reservation.generate_headers()
    assert(headers['Content-Type'] == 'application/json')
    assert(headers['X-API-Key'] == 'l7xx0a43088fe6254712b10787646d1b298e')


@my_vcr.use_cassette()
def test_reservation_lookup():
    try:
        r.lookup_existing_reservation()
    except Exception:
        pytest.fail("Error looking up reservation")


@my_vcr.use_cassette()
def test_checkin():
    try:
        r.checkin()
    except Exception:
        pytest.fail("Error checking in")


@my_vcr.use_cassette()
def test_checkin_without_passes():
    try:
        r.checkin()
    except Exception:
        pytest.fail("Error checking in")


@my_vcr.use_cassette()
def test_openflights_api():
    assert southwest.timezone_for_airport('LAX').zone == "America/Los_Angeles"


@my_vcr.use_cassette()
def test_cli():
    try:
        checkin.auto_checkin('XXXXXX', 'John', 'Smith')
    except Exception:
        pytest.fail("cli error")
