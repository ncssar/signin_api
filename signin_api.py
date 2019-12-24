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
#  12-11-19   TMG     0.9   first upload to cloud
#
# #############################################################################

import flask
from flask import request, jsonify
# import sqlite3
import json
import sys
from pathlib import Path

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# on pythonanywhere, the relative path ./sign-in should be added instead of ../sign-in
#  since the current working dir while this script is running is /home/caver456
#  even though the script is in /home/caver456/signin_api
# while it should be ok to load both, it's a lot cleaner to check for the
#  one that actually exists
p=Path('../sign-in')
if not p.exists():
    p=Path('./sign-in')
pr=str(p.resolve())
sys.path.append(pr)
app.logger.info("python search path:"+str(sys.path))

from signin_db import *

# response = jsonified list of dict and response code
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
    r=sdbNewEvent(d)
    app.logger.info("sending response from api_newEvent:"+str(r))
    return jsonify(r)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>SignIn Database API</h1>
<p>API for interacting with the sign-in databases</p>'''

# response = jsonified list
@app.route('/api/v1/events',methods=['GET'])
def api_getEvents():
    lastEditSince=request.args.get("lastEditSince",0)
    eventStartSince=request.args.get("eventStartSince",0)
    nonFinalizedOnly=request.args.get("nonFinalizedOnly",False)
    nonFinalizedOnly=str(nonFinalizedOnly).lower()=='true' # convert to boolean
    app.logger.info("events called: lastEditSince="+str(lastEditSince)
            +" eventStartSince="+str(eventStartSince)
            +" nonFinalizedOnly="+str(nonFinalizedOnly))
    return jsonify(sdbGetEvents(lastEditSince,eventStartSince,nonFinalizedOnly))

@app.route('/api/v1/events/<int:eventID>', methods=['GET'])
def api_getEvent(eventID):
    return jsonify(sdbGetEvent(eventID))
#     return "<html>stuff<html>"

# @app.route('/api/v1/events/current', methods=['GET'])
# def api_all():
#     return all()

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
    app.logger.info("put called for event "+str(eventID))
    if not request.json:
        app.logger.info("no json")
        return "<h1>400</h1><p>Request has no json payload.</p>", 400
    if type(request.json) is str:
        d=json.loads(request.json)
    else: #kivy UrlRequest sends the dictionary itself
        d=request.json
    return jsonify(sdbAddOrUpdate(eventID,d))

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

# app.run() must be run on localhost flask and LAN flask, but not on cloud (WSGI);
#  check to see if the resolved path directory contains '/home'; this may
#  need to change when LAN server is incorporated, since really it is just checking
#  for linux vs windows
if '/home' not in pr:
    app.run()
