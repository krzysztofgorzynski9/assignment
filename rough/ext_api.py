import requests
import json
import logging

from .config import settings

key = settings['translation_api_key']
username = settings['translation_user']
url = settings['translation_url']
headers = {
    'Authorization': f'ApiKey {username}:{key}',
    'Content-Type': 'application/json'
}


def unbabel_post(endpoint, payload):
    res = requests.post(
            url + f'/{endpoint}/',
            headers=headers,
            data=json.dumps(payload))
    try:
        return res.json()
    except:
        logging.exception("Couldn't decode JSON: {}".format(res.content))
        raise


def unbabel_get(endpoint, uid=None, **params):
    if uid:
        spec_url = url + f'/{endpoint}/{uid}/'
    else:
        spec_url = url + f'/{endpoint}/'
    res = requests.get(
            spec_url,
            headers=headers,
            params=params)
    try:
        return res.json()
    except:
        logging.exception("Couldn't decode JSON: {}".format(res.content))
        raise
