# #############################################################################
#
#  signin_api.py - host web API code for sign-in app
#
#  sign-in is developed for Nevada County Sheriff's Search and Rescue
#    Copyright (c) 2019 Tom Grundy
#
#   sign-in (c) 2019 Tom Grundy, using kivy and buildozer
#
#  http://github.com/ncssar/sign-in
#
#  Contact the author at nccaves@yahoo.com
#   Attribution, feedback, bug reports and feature requests are appreciated
#
#  REVISION HISTORY
#-----------------------------------------------------------------------------
#   DATE   | AUTHOR | VER |  NOTES
#-----------------------------------------------------------------------------
#
# #############################################################################

import flask
from flask import request, jsonify
# import sqlite3
import json

from signin_db import *

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/api/v1/events/new', methods=['POST'])
def api_newEvent():
    app.logger.info("new called")
    if not request.json:
        app.logger.info("no json")
        return "<h1>400</h1><p>Request has no json payload.</p>", 400
    if type(request.json) is str:
        d=json.loads(request.json)
    else: #kivy UrlRequest sends the dictionary itself
        d=request.json
    return newEvent(d)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>SignIn Database API</h1>
<p>API for interacting with the sign-in databases</p>'''

@app.route('/api/v1/events/<int:eventID>', methods=['GET'])
def api_getEvent(eventID):
    return getEvent(eventID)

@app.route('/api/v1/events/current', methods=['GET'])
def api_all():
    return all()

@app.route('/api/v1/events/<int:eventID>/html', methods=['GET'])
def api_getEventHTML(eventID):
    return getEventHTML(eventID)

# it's cleaner to let the host decide whether to add or to update;
# if ID, Agency, Name, and InEpoch match those of an existing record,
#  then update that record; otherwise, add a new record;
# PUT seems like a better fit than POST based on the HTTP docs
#  note: only store inEpoch to the nearest hunredth of a second since
#  comparison beyond 5-digits-right-of-decimal has shown truncation differences

@app.route('/api/v1/events/<int:eventID>', methods=['PUT'])
def api_add_or_update(eventID):
    app.logger.info("put1")
    app.logger.info("put called for event "+str(eventID))
    if not request.json:
        app.logger.info("no json")
        return "<h1>400</h1><p>Request has no json payload.</p>", 400
    if type(request.json) is str:
        d=json.loads(request.json)
    else: #kivy UrlRequest sends the dictionary itself
        d=request.json
    return add_or_update(eventID,d)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


app.run()