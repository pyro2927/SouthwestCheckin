import requests
import sys

API_KEY = 'l7xxb3dcccc4a5674bada48fc6fcf0946bc8'
USER_EXPERIENCE_KEY = 'AAAA3198-4545-46F4-9A05-BB3E868BEFF5'
BASE_URL = 'https://mobile.southwest.com/api/'
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
