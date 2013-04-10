import MySQLdb
import os
from tempfile import NamedTemporaryFile

from flask import Blueprint, request, session, g, redirect, url_for, abort, render_template, flash, jsonify, abort

from PIL import Image

from imageSplit import divLines, splitImage

ALLOWED_IMAGE_EXTENSIONS = set(['jpeg', 'jpg', 'gif', 'png', 'bmp'])

# Make this api a blueprint
pageops = Blueprint('pageops', __name__)

def allowed_file(filename):
    return '.' in filename and \
	  filename.rsplit('.', 1)[1] in ALLOWED_IMAGE_EXTENSIONS

@pageops.route('/get_points', methods=['POST'])
def get_points():
    '''
    Get points is a flask endpoint that takes one argument, file
    which is an image uploaded via http
    It returns a json object with the resulting dividing lines and the
    temporary name for the image
    '''
    file = request.files['file']
    if file and allowed_file(file.filename):
        # create a temporary file
        f = NamedTemporaryFile(delete=False)
        name = f.name
        f.write(file.read())
        f.close()
        # get the dividing points for the page
        i = Image.open(name)
        divs = divLines(i)
        del i
        # return the dividing points and the name of the page in json form
        return jsonify(
            name = name,
            vlines = divs[0],
            hlines = divs[1])
    else:
        return 'request failed'
        
        
