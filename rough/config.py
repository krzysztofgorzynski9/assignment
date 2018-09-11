import time
import logging
import configparser
from collections import defaultdict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.exc import IntegrityError 


settings = {
    'key': 'dummy-key',
    'unbabel_connect': False,
    'callback_url': '',
    'translation_user': '',
    'translation_api_key': '',
    'translation_url': '',
    'api_handler': None
}

def load_config():
    config = configparser.ConfigParser()
    config.read('/home/app/cfg/app.ini')
    if not 'settings' in config:
        return
    for entry in settings.keys():
        if entry in config['settings']:
            settings[entry] = config['settings'][entry]


def create_postgres_session():
    engine = create_engine('postgresql://db/postgres')
    max_tries = 10
    ntry = 0
    while ntry <= max_tries:
        try:
            engine.connect()
        except:
            ntry += 1
            time.sleep(3)
            logging.info("Couldn't establish connection with database. Retrying...")
        else:
            logging.info("Connection with database established.")
            break

    Base = declarative_base()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)

    return engine, Session(), Base

class TestSession:
    def __init__(self):
        self.reset()

    def rollback(self): pass
    def commit(self): pass

    def query(self, cls):
        self._current_cls = cls
        return self

    def all(self):
        return list(self._db[self._current_cls].values())

    def filter(self, cond):
        return self

    def add(self, obj):
        if len(self._failures) > 0:
            raise self._failures.pop(0)
        else:
            self._db[type(obj)][obj.id] = obj

    def get(self, ob_id):
        collection = self._db[self._current_cls]
        res = None
        if ob_id in collection:
            res = collection[ob_id]
        return res

    def one(self):
        return list(self._db[self._current_cls].values())[-1]

    def reset(self):
        self._db = defaultdict(dict)
        self._failures = []

    def register_failure(self, failure_type):
        failures = {
            'foreign-key': IntegrityError('', '', '')
        }
        self._failures.insert(0, failures[failure_type])


class DBsession:
    """
    Database session class intended to decouple the API
    from the database implementation. Create subclasses
    of this class when running unit tests
    """
    @staticmethod
    def session():
        if hasattr(DBsession, '_session'):
            return DBsession._session
        else:
            raise AttributeError("Create db session first using method provided by DBsession class.")

    def base():
        if hasattr(DBsession, '_base'):
            return DBsession._base
        else:
            raise AttributeError("Create db session first using method provided by DBsession class.")

    @staticmethod
    def create_postgres_session():
        engine, session, base = create_postgres_session()
        DBsession._session = session
        DBsession._base = base
        DBsession._engine = engine

    @staticmethod
    def prepare_db():
        DBsession._base.metadata.create_all(DBsession._engine)

    @staticmethod
    def create_test_session():
        DBsession._session = TestSession()
        DBsession._base = declarative_base()

