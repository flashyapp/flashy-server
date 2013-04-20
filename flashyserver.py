# imports
from __future__ import with_statement
from contextlib import closing

import MySQLdb
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

import logging
import os

# configuration defaults
DATABASE = 'Default'
DEBUG = True
SECRET_KEY = 'developer key'
USERNAME = 'dbUserName'
PASSWORD = 'dbPassword'
ALLOWED_IMAGE_EXTENSIONS = set(['jpeg', 'jpg', 'gif', 'png', 'bmp'])
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIRECTORY = "user_images/"
LOG_FILE = "flashy_server.log"

# create the application
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object('settings')


# Set the logger configuration
logging.basicConfig(filename=LOG_FILE, format='%(levelname)s:%(message)s', level=logging.DEBUG)

# Blueprint imports
from testops import testops
from userops import userops
from deckops import deckops

# Blueprints for the various parts of the application
app.register_blueprint(testops)
# app.register_blueprint(pageops, url_prefix='/page') not used any longer
app.register_blueprint(userops, url_prefix='/user')
app.register_blueprint(deckops, url_prefix='/deck')

def connect_db():
    return MySQLdb.connect(
	user=app.config['USERNAME'],
	passwd=app.config['PASSWORD'],
	db=app.config['DATABASE'])

def init_db():
    from pprint import pprint
    with closing(connect_db()) as db:
	with app.open_resource('schema.sql') as f:
	    cur = db.cursor()
            cur.connection.autocommit(True)
            for query in f.read().split(';'):
                print query
                cur.execute(query)
                db.commit()
                
@app.before_request
def before_request():
    g.db = connect_db()
    g.cur = g.db.cursor()

@app.teardown_request
def teardown_request(exception):
    g.db.commit()               # this is bad but preventative
    g.db.close()


if __name__ == "__main__":
    logging.debug('Starting test server')
    app.run()





