import json
import logging
import gevent
import traceback
from gevent import Greenlet, monkey
monkey.patch_all()

from flask import Flask, request, jsonify
from flask_cors import CORS

from .models import Script
from .config import settings


application = Flask(__name__)
# In production environment we want that only our UI to communicate with the backend.
CORS(application)


class APIerror(Exception):
    status_code = 400


class ObjectNotExist(APIerror):
    def to_dict(self):
        return {'message': "Object based on given query doesn't exist"}


class MissingParameter(APIerror):
    def to_dict(self):
        return {'message': "Missing parameter"}


def update_pending_scripts(api_handler):
    pending_scripts = [s.unbabel_id for s in Script.get_by_status('pending') if s.unbabel_id != '']
    pending_external_scripts = api_handler.pending_scripts()
    # If the external API doesn not contain a script which is pending
    # in our database, it means it has been already translated.
    translated_scripts = set(pending_scripts).difference(pending_external_scripts)
    if len(translated_scripts) > 0:
        translated_content = api_handler.fetch_translations(translated_scripts)
        Script.set_translated(translated_content)

@application.errorhandler(APIerror)
def handle_missing_parameter(err):
    resp = jsonify(err.to_dict())
    resp.status_code = err.status_code
    return resp

@application.route("/trans")
def hello():
    return "Hello World!"

@application.route("/trans/script", methods=['GET'])
def get_script():
    script_id = request.args.get('id')
    if script_id is None or len(script_id) == 0:
        raise MissingParameter('id')
    script = Script.get(sid=script_id)
    if script is None:
        raise ObjectNotExist
    return jsonify(script.to_dict())

@application.route('/trans/scripts', methods=['GET'])
def get_scripts():
    ids = request.args.get('ids')
    if ids:
        ids = json.loads(ids)
        scripts = Script.get_many(ids)
        # scripts = Script.get_all()
    else:
        scripts = Script.get_all()
    res = [s.to_dict() for s in scripts]
    return jsonify(res)

@application.route('/trans/wait')
def wait():
    gevent.sleep(5)
    return jsonify('ok')

@application.route("/trans/script", methods=['POST'])
def add_script():
    data = json.loads(request.data)
    content = data['content']
    new_id = data['newId']
    new_script = Script.create(
            sid=new_id,
            status='pending',
            content=content)
    if len(settings['translation_url']) > 0:
        try:
            uid = settings['api_handler'].request_translation(content)
            new_script.set_ext_id(ext_id=uid)
            return jsonify({'status': 'ok'})
        except:
            traceback.exception("Error during adding a script")
            return jsonify({'status': 'failed'})
    else:
        return jsonify({'status': 'ok'})
