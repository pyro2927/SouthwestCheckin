import requests
import json
import pytz


def timezone_for_airport(airport_code):
    tzrequest = {'iata': airport_code,
                 'country': 'ALL',
                 'db': 'airports',
                 'iatafilter': 'true',
                 'action': 'SEARCH',
                 'offset': '0'}
    tzresult = requests.post("https://openflights.org/php/apsearch.php", tzrequest)
    airport_tz = pytz.timezone(json.loads(tzresult.text)['airports'][0]['tz_id'])
    return airport_tz
