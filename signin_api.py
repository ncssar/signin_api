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
import sqlite3
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True
        
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def q(query):
#     app.logger.info("q called: "+query)
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    r=cur.execute(query).fetchall()
    conn.commit()
#     app.logger.info("  result:" +str(r))
    return r


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''


@app.route('/api/v1/events/current', methods=['GET'])
def api_all():
#     conn = sqlite3.connect('test.db')
#     conn.row_factory = dict_factory
#     cur = conn.cursor()
#     all = cur.execute('SELECT * FROM SignIn;').fetchall()
# 
#     return jsonify(all)
    return jsonify(q('SELECT * FROM SignIn;'))


# it's cleaner to let the host decide whether to add or to update;
# if ID, Agency, Name, and InEpoch match those of an existing record,
#  then update that record; otherwise, add a new record;
# PUT seems like a better fit than POST based on the HTTP docs
#  note: only store inEpoch to the nearest hunredth of a second since
#  comparison beyond 5-digits-right-of-decimal has shown truncation differences

@app.route('/api/v1/events/current', methods=['PUT'])
def api_add_or_update():
    app.logger.info("put called")
    if not request.json:
        app.logger.info("no json")
        return "<h1>400</h1><p>Request has no json payload.</p>", 400
    d=json.loads(request.json)
#     d['InEpoch']=round(d['InEpoch'],2)
#     d['OutEpocj']=round(d['OutEpoch'],2)
    
    # query builder from a dictionary that allows for different data types
    #  https://stackoverflow.com/a/54611514/3577105
#     colVal="({columns}) VALUES {values}".format(
#                 columns=', '.join(d.keys()),
#                 values=tuple(d.values())
#             )
    colList="({columns})".format(
                columns=', '.join(d.keys()))
    valList="{values}".format(
                values=tuple(d.values()))        
    # 1. find any record(s) that should be modified
    condition="ID = '{id}' AND Name = '{name}' AND Agency = '{agency}' AND InEpoch = '{inEpoch}'".format(
            tablename='SignIn',id=d['ID'],name=d['Name'],agency=d['Agency'],inEpoch=d['InEpoch'])
    query="SELECT * FROM {tablename} WHERE {condition};".format(
            tablename='SignIn',condition=condition)
    app.logger.info('query:'+query)
    r=q(query)
    app.logger.info("result:"+str(r))
    if len(r)==0: # no results: this is a new sign-in; add a new record
        # query builder from a dictionary that allows for different data types
        #  https://stackoverflow.com/a/54611514/3577105
#         query="INSERT INTO {tablename} ({columns}) VALUES {values};" .format(
#                 tablename='SignIn',
#                 columns=', '.join(d.keys()),
#                 values=tuple(d.values())
#             )
        query="INSERT INTO {tablename} {colList} VALUES {valList};".format(
                tablename='SignIn',
                colList=colList,
                valList=valList)
        app.logger.info("query string: "+query)
        q(query)
    elif len(r)==1: # one result found; this is a sign-out; modify existing record
        # UPDATE .. SET () = () syntax is only supported for sqlite3 3.15.0 and up;
        #  pythonanywhere only has 3.11.0, so, use simpler queries instead
#       query="UPDATE {tablename} SET {colList} = {valList} WHERE {condition};".format(
#               tablename='SignIn',
#               colList=colList,
#               valList=valList,
#               condition=condition)
        query="UPDATE {tablename} SET ".format(tablename='SignIn')
        for key in d.keys():
            query+="{col} = '{val}', ".format(
                col=key,
                val=d[key])
        query=query[:-2] # get rid of the final comma and space
        query+=" WHERE {condition};".format(condition=condition)
        app.logger.info("query string: "+query)
        q(query)
    else:
        return jsonify({'error': 'more than one record in the host database matched the ID,Name,Agency,InEpoch values from the sign-in action'}), 405

    return jsonify({'query': 'ok'}), 200

# @app.route('/api/v1/events/current/add', methods=['POST'])
# def api_add():
#     app.logger.info("post called")
# #     app.logger.info("request.data:"+str(request.get_data()))
#     if not request.json:
#         app.logger.info("no json")
#         return "<h1>400</h1><p>Request has no json payload.</p>", 400
# #     app.logger.info("post2")
# #     app.logger.info("json:"+str(json.loads(request.json)))
#     d=json.loads(request.json)
# #     app.logger.info("dict:"+str(d))
# 
#     # query builder from a dictionary that allows for different data types
#     #  https://stackoverflow.com/a/54611514/3577105
#     query="INSERT INTO {tablename} ({columns}) VALUES {values};" .format(
#             tablename='SignIn',
#             columns=', '.join(d.keys()),
#             values=tuple(d.values())
#         )
# 
#     app.logger.info("query string: "+query)
#     
#     conn = sqlite3.connect('test.db')
#     conn.row_factory = dict_factory
#     cur = conn.cursor()
#     cur.execute(query)
#     conn.commit()
#     
#     return jsonify({'query': 'ok'}), 201


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


# @app.route('/api/v1/resources/books', methods=['GET'])
# def api_filter():
#     query_parameters = request.args
# 
#     id = query_parameters.get('id')
#     published = query_parameters.get('published')
#     author = query_parameters.get('author')
# 
#     query = "SELECT * FROM books WHERE"
#     to_filter = []
# 
#     if id:
#         query += ' id=? AND'
#         to_filter.append(id)
#     if published:
#         query += ' published=? AND'
#         to_filter.append(published)
#     if author:
#         query += ' author=? AND'
#         to_filter.append(author)
#     if not (id or published or author):
#         return page_not_found(404)
# 
#     query = query[:-4] + ';'
# 
#     conn = sqlite3.connect('books.db')
#     conn.row_factory = dict_factory
#     cur = conn.cursor()
# 
#     results = cur.execute(query, to_filter).fetchall()
# 
#     return jsonify(results)

app.run()