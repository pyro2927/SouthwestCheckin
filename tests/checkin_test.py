import json
import pytest
import requests
import southwest
from datetime import datetime, timedelta
from .my_vcr import custom_vcr
from pytz import timezone, utc
from tzlocal import get_localzone

my_vcr = custom_vcr()

@my_vcr.use_cassette()
def test_checkin():
    r = southwest.Reservation('XXXXXX', 'John', 'Smith')
    try:
        r.checkin()
    except Exception:
        pytest.fail("Error checking in")


def test_timezone_localization():
    tz = timezone('America/Los_Angeles')
    date = tz.localize(datetime.strptime('2018-01-01 13:00', '%Y-%m-%d %H:%M'))
    assert date.strftime('%z') == '-0800'


@my_vcr.use_cassette()
def test_openflights_api():
    tzrequest = {'iata': 'LAX',
                 'country': 'ALL',
                 'db': 'airports',
                 'iatafilter': 'true',
                 'action': 'SEARCH',
                 'offset': '0'}
    tzresult = requests.post("https://openflights.org/php/apsearch.php", tzrequest)
    airport_tz = timezone(json.loads(tzresult.text)['airports'][0]['tz_id'])
    assert airport_tz.zone == "America/Los_Angeles"
