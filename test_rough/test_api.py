import pytest

from rough.config import DBsession
DBsession.create_test_session()


from rough.api import application, get_script, MissingParameter
from rough.api import update_pending_scripts
from rough.models import Script


@pytest.fixture
def db():
    DBsession.create_test_session()
    yield DBsession.session()
    DBsession.session().reset()

@pytest.fixture
def app():
    application.testing = True
    return application.test_client()

@pytest.fixture
def ext_api():
    class DummyAPI: 
        def pending_translations(self):
            return []

        def fetch_translations(self, uids):
            return [('uid', 'Conteudo do teste')]

    return DummyAPI()
        
def test_id_not_present(app):
    resp = app.get('/trans/script?id=')
    assert resp.status_code == 400
    assert b"Missing" in resp.data

def test_no_script_with_id(app):
    resp = app.get('/trans/script?id=not_exist')
    assert resp.status_code == 400
    assert b"exist" in resp.data

def test_create_script(app, db):
    resp = app.post('/trans/script?id=not_exist')

def test_sync_translated_scripts(db, app, ext_api):
    db.add(Script(
        id="abc",
        unbabel_id="uid",
        status='pending',
        content="Test content"))
    update_pending_scripts(ext_api)
    assert db.query(Script).one().status == 'translated'
    assert db.query(Script).one().translated == 'Conteudo do teste'

