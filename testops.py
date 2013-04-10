import MySQLdb
import os

from flask import Blueprint, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

ALLOWED_IMAGE_EXTENSIONS = set(['jpeg', 'jpg', 'gif', 'png', 'bmp'])
IMAGE_DIRECTORY = "/var/www/user_images/"
testops = Blueprint('testops', __name__)

@testops.route('/')
def show_info():
    return '''
    <!doctype html>
    <title> Dev Info </title>
    At this point this is left empty, don't worry about this page'''
    
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_IMAGE_EXTENSIONS

def create_filename(fid, filename):
    ext = filename.rsplit('.', 1)[1]
    fn = str(fid) + "." + ext
    return fn

@testops.route('/add_image', methods=['POST'])
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
            file.save(IMAGE_DIRECTORY
                      + filename)
            cur.execute("INSERT INTO photos VALUES(NULL, '{0}')".format(filename))
            cur.close()
        return jsonify(filename = filename)
@testops.route('/get_images', methods=['GET'])
def get_images():
    cur = g.db.cursor()
    cur.execute('SELECT * FROM photos')
    images = [ x[1] for x in cur.fetchall() ]
    cur.close()
    return jsonify(images = images)
    
@testops.route('/test_post', methods=['POST'])
def test_post():
    data = request.form['data']
    print data
    return jsonify(data = data)
