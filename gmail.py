from __future__ import print_function
import base64
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from scrapy.selector import Selector
from scrapy.http import HtmlResponse

import checkin

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'SW Checking App'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
            'sw-checkin.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """ Pulling Southwest emails from GMail """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().messages().list(userId='me').execute()
    messages = results.get('messages', [])

    if not messages:
        print('No emails found.')
    else:
        for message in messages:
            r = service.users().messages().get(userId='me',id=message['id'],format='full').execute()
            if "Southwest" in r['snippet'] and r['payload']['body'].has_key('data'):
                body = base64.urlsafe_b64decode(r['payload']['body']['data'].encode('UTF-8'))
                selector = Selector(text=body)
                divs = selector.css('span[style*="23972a"]::text').extract()
                if len(divs) > 0:
                    conf = divs[0].replace("\r", "").replace("\n", "").strip()
                    name = selector.css('div[style*="13px"]::text').extract()[13]
                    last_name, first_name = name.strip().split('/')
                    checkin.checkin(first_name, last_name, conf)

if __name__ == '__main__':
    main()