import checkin
import json
import pytest
import requests
from datetime import datetime 
from pytz import timezone

def test_checkin(requests_mock):
    requests_mock.register_uri('GET', '/api/mobile-misc/v1/mobile-misc/page/view-reservation/XXXX?first-name=John&last-name=Smith', text=open('fixtures/view-reservation.json', 'r').read())
    requests_mock.register_uri('GET', '/api/mobile-air-operations/v1/mobile-air-operations/page/check-in/XXXX?first-name=John&last-name=Smith', text=open('fixtures/checkin-get.json', 'r').read())
    requests_mock.register_uri('POST', '/api/mobile-air-operations/v1/mobile-air-operations/page/check-in', text=open('fixtures/checkin-post.json', 'r').read())
    requests_mock.register_uri('POST', '/php/apsearch.php', text=open('fixtures/openflights.json', 'r').read())
    assert checkin.auto_checkin('XXXX', 'John', 'Smith') == None

def test_timezone_localization():
    tz = timezone('America/Los_Angeles')
    date = tz.localize(datetime.strptime('2018-01-01 13:00', '%Y-%m-%d %H:%M'))
    assert date.strftime('%z') == '-0800'

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
