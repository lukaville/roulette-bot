import json

import requests
from telegram.ext.dispatcher import run_async

TRACK_URL = 'https://api.botan.io/track'
SHORTENER_URL = 'https://api.botan.io/s/'


class BotanAnalytics(object):
    def __init__(self, token):
        self.token = token

    @run_async
    def track(self, uid, message, name='Message'):
        try:
            requests.post(
                TRACK_URL,
                params={"token": self.token, "uid": uid, "name": name},
                data=json.dumps(message),
                headers={'Content-type': 'application/json'},
            )
        except requests.exceptions.Timeout:
            # set up for a retry, or continue in a retry loop
            pass
        except (requests.exceptions.RequestException, ValueError) as e:
            # catastrophic error
            print(e)
            pass

    def shorten_url(self, url, botan_token, user_id):
        """
        Shorten URL for specified user of a bot
        """
        try:
            return requests.get(SHORTENER_URL, params={
                'token': botan_token,
                'url': url,
                'user_ids': str(user_id),
            }).text
        except:
            return url
