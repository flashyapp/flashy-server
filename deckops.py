import MySQLdb
import os
import md5

from flask import Blueprint, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

from PIL import Image

import tempfile

from cStringIO import StringIO

from models import user, deck, card, resource

from imageSplit import divLines, splitImage

from settings import ALLOWED_IMAGE_EXTENSIONS

from utils import log_request, valid_params, id_generator, pairs

import logging

deckops = Blueprint('deckops', __name__, static_folder='deck_images')

####################
## Helper functions
####################

def allowed_file(filename):
    return '.' in filename and \
	  filename.rsplit('.', 1)[1] in ALLOWED_IMAGE_EXTENSIONS


####################
## Endpoints
####################

@deckops.route('/new/from_lists', methods=['POST'])
def new_from_cards():
    log_request(request)
    data = request.json
    
    if not valid_params(['username', 'deck_name', 'description', 'cards', 'session_id'], data):
        logging.debug("Missing parameters")
        return jsonify({'error' : 500})
        
    username = data['username']
    deckname = data['deck_name']
    desc     = data['description']
    cards    = data['cards']
    sId      = data['session_id']
    
    # authenticate the user
    uId = user.get_uId(username)
    if not user.verify(username, sId):
        return jsonify({'error' : 101})

    # create the deck in the database
    dId, deck_id = deck.new(deckname, uId, desc)

    # create the cards
    for c in cards:
        card.new(dId, c['sideA'], c['sideB'])

    ret = deck.get_deck(dId)
    ret['error'] = 0            # set error code
    return jsonify(ret)

@deckops.route('/new/upload_image', methods=['POST'])
def new_upload_image():
    log_request(request)

    if not valid_params(['username', 'session_id'], request.form) or\
       not valid_params(['file'], request.files):
        logging.debug("Missing parameters")
        return jsonify({'error' : 500})
        
    username = request.form['username']
    sId = request.form['session_id']
    fil = request.files['file']

    
    # check session before upload
    if not user.verify(username, sId):
        logging.debug("Invalid username or session id")
        return jsonify({'error' : 101})

    if fil and allowed_file(fil.filename):
        # get the file extension
        ext = os.path.splitext(fil.filename)[1]
        # create a temporary file
        f = tempfile.NamedTemporaryFile(delete=False, dir="/var/www/resources/tmp/", suffix="{0}".format(ext))
        name = os.path.basename(f.name)
        f.write(fil.read())
        f.close()
        # get the dividing points for the page
        i = Image.open(f.name)
        divs = divLines(i)
        del i
        # return the dividing points and the name of the page in json form
        return jsonify(
            name = name,
            divs = divs,
            error  = 0)
    else:
        logging.debug("Image processing failed, invalid filetype?")
        return jsonify({'error' : 200})

        
@deckops.route('/new/from_image', methods=['POST'])
def new_from_image():
    log_request(request)
    data = request.json

    if not valid_params(['username', 'deck_name', 'description', 'session_id', 'name', 'divs'], data):
        logging.debug("Missing parameters")
        return jsonify({'error' : 500})
        
    username = data['username']
    deckname = data['deck_name']
    desc     = data['description']
    sId      = data['session_id']

    filename = data['name']
    
    uId = user.get_uId(username)
    
    if not user.verify(username, sId):
        return jsonify({'error' : 101})
        
    if not filename or not os.path.exists("/var/www/resources/tmp/{0}".format(filename)):
        return jsonify({'error' : 201})
        
    # create the new deck in the database
    dId, deck_id = deck.new(deckname, uId, desc)

    # split the temp image
    i = Image.open("/var/www/resources/tmp/{0}".format(filename))
    imgs = splitImage(i, data['divs'])

    for row in imgs:
        # pairwise collect the cards
        img_pairs =  pairs(row)
        for p in img_pairs:
            cId = card.new(dId, "", "")
            # String IO for file in memory
            atmp = StringIO()
            p[0].save(atmp, format="JPEG")
            atmp.seek(0)
            a_id = resource.new(atmp, id_generator(), cId)[1]
            sideA = '<img src="[FLASHYRESOURCE:{0}]" />'.format(a_id)

            if p[1] != None:
                btmp = StringIO()
                p[1].save(btmp, format="JPEG")
                btmp.seek(0)
                b_id = resource.new(btmp, id_generator(), cId)[1]
                sideB = '<img src="[FLASHYRESOURCE:{0}]" />'.format(b_id)
            else:
                sideB = '[FLASHYRESOURCE:00000000]'
                
            card.modify(cId, sideA, sideB)

    os.unlink("/var/www/resources/tmp/{0}".format(filename))        # let the filesystem delete the temp file
    d = deck.get_deck(dId);
    return jsonify({'deck': d, 'error': 0})


@deckops.route('/<deck_id>/modify', methods=['POST'])
def deck_modify(deck_id):
    log_request(request)
    
    data = request.json
    if not valid_params(['username', 'name', 'description', 'session_id'], data):
        logging.debug("Missing parameters")
        return jsonify({'error' : 500})
        
    username = data['username']
    deckname = data['name']
    desc     = data['description']
    sId      = data['session_id']

    # authenticate the user
    if not user.verify(username, sId):
        return jsonify({'error' : 101})

    dId = deck.get_id(deck_id)
    
    # check that the deck exists
    if not deck.exists(dId):
        return jsonify({'error' : 300})


    deck.modify(dId, deckname, desc)
    return jsonify({'error': 0})

    
@deckops.route('/<deck_id>/get', methods=['POST'])
def get_deck(deck_id):
    log_request(request)

    data = request.json
    if not valid_params(['username', 'session_id'], data):
        logging.debug("Missing parameters")
        return jsonify({'error' : 500})
        
    username = data['username']
    sId = data['session_id']
    
    if not user.verify(username, sId):
        return jsonify({'error' : 101})

    dId = deck.get_id(deck_id)
        
    ret = deck.get_deck(dId)
    ret['error'] = 0            # append the error code
    
    return jsonify(ret)

@deckops.route('/<deck_id>/')
@deckops.route('/<deck_id>/delete', methods=['POST'])
def delete_deck(deck_id):
    log_request(request)
    
    data = request.json
    if not valid_params(['username', 'session_id'], data):
        logging.debug("Missing parameters")
        return jsonify({'error' : 500})
        
    username = request.json['username']
    sId = request.json['session_id']
    
    if not user.verify(username, sId):
        logging.debug("Invalid username or session_id")
        return jsonify({'error' : 101})    

    dId = deck.get_id(deck_id)
    
   # check that the deck exists
    if not deck.exists(dId):
        logging.debug("Deck does not exist")
        return jsonify({'error' : 300})
        
    ret = deck.delete(dId)

    if ret == 1:
        logging.debug("Deleted deck successfully")
        return jsonify({'error' : 0})
    else:
        logging.debug("Failed to delete deck")
        return jsonify({'error' : 300})

@deckops.route('/get_decks', methods=['POST'])
def deck_get_decks():
    log_request(request)

    data = request.json
    
    if not valid_params(['username', 'session_id'], data):
        logging.debug("Missing parameters")
        return jsonify({'error' : 500})
        
    username = request.json['username']
    session_id = request.json['session_id']
    
    # verify session
    if not user.verify(username, session_id):
        logging.debug("Invalid username or session")
        return jsonify({'error' : 101})
        
    uId = user.id_name(username)

    decks = deck.get_decks_by_uId(uId)
    ret = {'decks' : []}
    for d in decks:
        ret['decks'].append({'name' : d[0],
                             'deck_id' : d[1],
                             'description' : d[2]})

    ret['error'] = 0
    return jsonify(ret)
    
@deckops.route('/<deck_id>/card/create', methods=['POST'])
def deck_create_card(deck_id):
    log_request(request)
    username = request.json['username']
    sId = request.json['session_id']
    sideA = request.json['sideA']
    sideB = request.json['sideB']

    # verify session
    if not user.verify(username, sId):
        return jsonify({'error' : 101})
        
    dId = deck.get_id(deck_id)
    
    # check that the deck exists
    if not deck.exists(dId):
        return jsonify({'error' : 300})

    ret = card.new(dId, sideA, sideB)
    
    return jsonify({'error' : 0})


@deckops.route('/<deck_id>/card/modify', methods=['POST'])
def deck_modify_card(deck_id):
    log_request(request)
    username = request.json['username']
    sId = request.json['session_id']
    sideA = request.json['sideA']
    sideB = request.json['sideB']
    index = request.json['index']

    # verify session
    if not user.verify(username, sId):
        logging.debug("Invalid username or session_id")
        return jsonify({'error' : 101})
        
    dId = deck.get_id(deck_id)
    
    # check that the deck exists
    if not deck.exists(dId):
        logging.debug("Deck does not exist")
        return jsonify({'error' : 300})

    
    cId = card.get_cId(dId, index)
    ret = card.modify(cId, sideA, sideB)
    
    if ret == 1:
        return jsonify({'error' : 0})
    else:
        return jsonify({'error' : 400}) # no idea why this would happen


@deckops.route('/<deck_id>/card/delete', methods=['POST'])
def deck_delete_card(deck_id):
    log_request(request)
    username = request.json['username']
    sId = request.json['session_id']
    index = request.json['index']

    # verify session
    if not user.verify(username, sId):
        logging.debug("Invalid username or session_id")
        return jsonify({'error' : 101})

    dId = deck.get_id(deck_id)
    
    # check that the deck exists
    if not deck.exists(dId):
        logging.debug("Deck does not exist")
        return jsonify({'error' : 300})

    dId = deck.get_id(deck_id)
    cId = card.get_cId(dId, index)
    ret = card.delete(cId)
    
    if ret == 1:
        return jsonify({'error' : 0})
    else:
        return jsonify({'error' : 400}) # no idea why this would happen

@deckops.route('/<deck_id>/card/get_resources', methods=['POST'])
def deck_card_get_resources(deck_id):
    log_request(request)
    username = request.json['username']
    sId = request.json['session_id']
    index = request.json['index']

    # verify session
    if not user.verify(username, sId):
        logging.debug("Invalid username or session_id")
        return jsonify({'error' : 101})

    dId = deck.get_id(deck_id)
    
    # check that the deck exists
    if not deck.exists(dId):
        logging.debug("Deck does not exist")
        return jsonify({'error' : 300})

    cId = card.get_cId(dId, index)
    
    resources = card.get_resources(cId)
    res = [{'resource_id' : rId, 'name' : name, 'path' : path} for rId, name, path, hashval in resources]
    return jsonify(resources = res, error = 0)

@deckops.route('/<deck_id>/card/add_resource', methods=['POST'])
def deck_card_add_resource(deck_id):
    log_request(request)
    username = request.form['username']
    sId = request.form['session_id']
    index = request.form['index']
    f = request.files['file']
    
    # verify session
    if not user.verify(username, sId):
        logging.debug("Invalid username or session_id")
        return jsonify({'error' : 101})

    dId = deck.get_id(deck_id)

    if not deck.exists(dId):
        logging.debug("Deck does not exist")
        return jsonify({'error' : 300})

    cId = card.get_cId(dId, index)
    rows, resource_id = resource.new(f, f.filename, cId)
    return jsonify(resource_id = resource_id)

@deckops.route('/<deck_id>/card/delete_resource', methods=['POST'])
def deck_card_delete_resource(deck_id):
    log_request(request)
    username = request.json['username']
    sId = request.json['session_id']
    resource_id = request.json['resource_id']

    # verify session
    if not user.verify(username, sId):
        logging.debug("Invalid username or session_id")
        return jsonify({'error' : 101})

    # verify the user owns the deck
    
    resource.delete(resource_id)
    return jsonify({'error' : 0})
