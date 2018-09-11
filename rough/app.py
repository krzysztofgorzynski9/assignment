import gevent
from gevent import Greenlet, monkey
monkey.patch_all()
import logging
logging.basicConfig(level=logging.DEBUG)

import requests

from .config import DBsession, load_config, settings
load_config()
DBsession.create_postgres_session()

from .api import application, update_pending_scripts
from .models import Script
from .ext_api import unbabel_get, unbabel_post

class ExtAPI:
    def pending_scripts(self):
        objects =  unbabel_get('translation', status='pending')['objects']
        return [ob['uid'] for ob in objects]

    def fetch_translations(self, uids):
        translations = []
        for uid in uids:
            # TODO: make this asynchronous by spawning several greenlets
            resp = unbabel_get('translation', uid=uid)
            if resp['status'] == 'completed':
                translated = resp['translatedText']
                translations.append((uid, translated))
        return translations

    def request_translation(self, content):
        payload = {
            'text': content,
            'text_format': 'text',
            'source_language': 'en',
            'target_language': 'es'
        }
        return unbabel_post('translation', payload)['uid']


class OfflineAPI:
    def pending_scripts(self):
        return []

    def fetch_translations(self, uids):
        return [(s.unbabel_id, s.content + ' -- translated') for s in Script.get_all()]

    def request_translation(self, content):
        import random
        return str(random.randint(0, 10000))


def sync_entries():
    """
    Due to initial number of translations (over 30k) associated with the key, the app
    doesn't synchronize all these scripts with its internal database.
    Instead, we only keep track of the requests that originated from this instance.
    """
    import time

    while True:
        try:
            update_pending_scripts(settings['api_handler'])
        except:
            logging.exception("Error occured during synchronisation")
        time.sleep(60)

DBsession.prepare_db()
g = Greenlet.spawn(sync_entries)
settings['api_handler'] = ExtAPI()

if __name__ == "__main__":

    from gevent import pywsgi as wsgi
    logging.info("Running gevent wsgi server")
    server = wsgi.WSGIServer(('0.0.0.0', 8000), application)
    server.serve_forever()
