from time import sleep
import requests
import sys

API_KEY = 'l7xx0a43088fe6254712b10787646d1b298e'
USER_EXPERIENCE_KEY = 'f6d3cb28-ed9c-4a89-aca7-cb39a9d75'
BASE_URL = 'https://mobile.southwest.com/api/'
CHECKIN_INTERVAL_SECONDS = 0.25
MAX_ATTEMPTS = 40

# Pulled from proxying the Southwest iOS App
headers = {'Host': 'mobile.southwest.com', 'Content-Type': 'application/json', 'X-API-Key': API_KEY, 'X-User-Experience-Id': USER_EXPERIENCE_KEY, 'Accept': '*/*'}


class Reservation():

    def __init__(self, number, first, last, notifications=[]):
        self.number = number
        self.first = first
        self.last = last
        self.notifications = []

    # You might ask yourself, "Why the hell does this exist?"
    # Basically, there sometimes appears a "hiccup" in Southwest where things
    # aren't exactly available 24-hours before, so we try a few times
    def safe_request(self, url, body=None):
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
                    sleep(CHECKIN_INTERVAL_SECONDS)
                    continue
                return data
        except ValueError:
            # Ignore responses with no json data in body
            pass

    def load_json_page(self, url, body=None):
        data = self.safe_request(url, body)
        if not data:
            return
        for k, v in list(data.items()):
            if k.endswith("Page"):
                return v

    def with_suffix(self, uri):
        return "{}{}{}?first-name={}&last-name={}".format(BASE_URL, uri, self.number, self.first, self.last)

    def lookup_existing_reservation(self):
        # Find our existing record
        return self.load_json_page(self.with_suffix("mobile-misc/v1/mobile-misc/page/view-reservation/"))

    def get_checkin_data(self):
        return self.load_json_page(self.with_suffix("mobile-air-operations/v1/mobile-air-operations/page/check-in/"))

    def checkin(self):
        data = self.get_checkin_data()
        info_needed = data['_links']['checkIn']
        url = "{}mobile-air-operations{}".format(BASE_URL, info_needed['href'])
        print("Attempting check-in...")
        confirmation = self.load_json_page(url, info_needed['body'])
        if len(self.notifications) > 0:
            self.send_notification(confirmation)
        return confirmation

    def send_notification(self, checkindata):
        if not checkindata['_links']:
            print("Mobile boarding passes not eligible for this reservation")
            return
        info_needed = checkindata['_links']['boardingPasses']
        url = "{}mobile-air-operations{}".format(BASE_URL, info_needed['href'])
        mbpdata = self.load_json_page(url, info_needed['body'])
        info_needed = mbpdata['_links']
        url = "{}mobile-air-operations{}".format(BASE_URL, info_needed['href'])
        print("Attempting to send boarding pass...")
        for n in self.notifications:
            body = info_needed['body'].copy()
            body.update(n)
            self.safe_request(url, body)
