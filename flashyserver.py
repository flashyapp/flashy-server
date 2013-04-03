# imports
from __future__ import with_statement
from contextlib import closing

import MySQLdb
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

# create the application
app = Flask(__name__)
# app.config.from_object(__name__)

app.config.from_envvar('FLASHY_SETTINGS', silent=True)

def connect_db():
    return MySQLdb.connect(
        user=app.config['USERNAME'],
        passwd=app.config['PASSWORD'],
        db=app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().execute(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def show_entries():
    cur = g.db.cursor()
    cur.execute('SELECT title, filename FROM photos ORDER BY id DESC')
    cur.close()
    photos = cur.fetchall()
    pprint(photos)
    return jsonify(photos)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_IMAGE_EXTENSIONS']
def create_filename(fid, filename):
    ext = filename.rsplit('.', 1)[1]
    fn = str(fid) + "." + ext
    return fn

@app.route('/add_image', methods=['POST'])
def add_image():
    file = request.files['file']
    if file and allowed_file(file.filename):
        # get the maximum id number for the table
        cur = g.db.cursor()
        cur.execute('SELECT MAX(id) AS max_id FROM photos')
        fid = cur.fetchall()[0][0]
        if fid == None:
            fid = 1
        else:
            fid += 1                # increment the max id number
        filename = create_filename(fid, file.filename)
        file.save(app.config['APP_ROOT'] +
                  app.config['IMAGE_DIRECTORY']
                  + filename)
        cur.execute("INSERT INTO photos VALUES(NULL, '{0}')".format(filename))
        cur.close()
        g.db.commit()
        return jsonify(filename = filename)

@app.route('/get_images', methods=['GET'])
def get_images():
    cur = g.db.cursor()
    cur.execute('SELECT * FROM photos')
    result = cur.fetchall()
    cur.close()
    g.db.commit()
    return jsonify(result)

if __name__ == "__main__":
    app.run()





