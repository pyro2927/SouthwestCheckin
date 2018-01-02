import pytest
import checkin
import requests_mock
from datetime import datetime 
from pytz import timezone

@requests_mock.Mocker()
def test_checkin(m):
    m.register_uri('GET', '/api/mobile-misc/v1/mobile-misc/page/view-reservation/XXXX?first-name=John&last-name=Smith', text=open('fixtures/view-reservation.json', 'r').read())
    m.register_uri('GET', '/api/mobile-air-operations/v1/mobile-air-operations/page/check-in/XXXX?first-name=John&last-name=Smith', text=open('fixtures/checkin-get.json', 'r').read())
    m.register_uri('POST', '/api/mobile-air-operations/v1/mobile-air-operations/page/check-in', text=open('fixtures/checkin-post.json', 'r').read())
    assert checkin.auto_checkin('XXXX', 'John', 'Smith') == None

def test_timzone_localization():
    tz = timezone('America/Los_Angeles')
    date = tz.localize(datetime.strptime('2018-01-01 13:00', '%Y-%m-%d %H:%M'))
    assert date.strftime('%z') == '-0800'
