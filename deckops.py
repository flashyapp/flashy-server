import MySQLdb
import os
import md5

from flask import Blueprint, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from PIL import Image
from models import user, deck, card

from imageSplit import divLines, splitImage

from settings import ALLOWED_IMAGE_EXTENSIONS

from utils import log_request, valid_params

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
    sId = requst.form['session_id']
    fil = request.files['file']

    
    # check session before upload
    if not user.verify(username, sId):
        logging.debug("Invalid username or session id")
        return jsonify({'error' : 101})

    if fil and allowed_file(fil.filename):
        # create a temporary file
        f = NamedTemporaryFile(delete=False)
        name = f.name
        f.write(fil.read())
        f.close()
        # get the dividing points for the page
        i = Image.open(name)
        divs = divLines(i)
        del i
        # return the dividing points and the name of the page in json form
        return jsonify(
            name = name,
            vlines = divs[0],
            hlines = divs[1],
            error  = 0)
    else:
        logging.debug("Image processing failed, invalid filetype?")
        return jsonify({'error' : 200})

        
@deckops.route('/new/from_image', methods=['POST'])
def new_from_image():
    log_request(request)
    data = request.json

    if not valid_params(['username', 'deck_name', 'description', 'session_id', 'name'], data):
        logging.debug("Missing parameters")
        return jsonify({'error' : 500})
        
    username = data['username']
    deckname = data['deck_name']
    desc     = data['description']
    sId      = data['session_id']

    filename = data['name']
    
    uId = get_uId(username)
    
    if not user.verify(username, sId):
        return jsonify({'error' : 101})
        
    if not filename or not os.path.exists(filename):
        return jsonify({'error' : 201})
        
    # create the new deck in the database
    dId, deck_id = deck.new(deckname, uId, desc)

    # Create a directory to hold the deck images
    # TODO: clean this up to use settings appropriately
    dirname = os.path.join(os.path.dirname(__file__),"deck_images", str(dId))
    os.mkdir(dirname)

    # split the temp image
    i = Image.open(filename)
    imgs = splitImage(i, (data['vlines'], data['hlines']))
    
    # save the images in the deck file
    filelist = []
    for i, img in enumerate(imgs):
        filename = str(i) + ".jpg"
        filelist.append(filename)
        img.convert('RGB').save(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),"deck_images",str(deck_id),filename))
    
    asides = filelist[:len(filelist)/2]
    bsides = filelist[len(filelist)/2:]
    for icard in zip(asides, bsides):
        cId = card.new(dId, "", "")
        sideA = '<img src="deck/{0}/card/{1}/resources/{2}" />'.format(deck_id, cId, icard[0])
        sideB = '<img src="deck/{0}/card/{1}/resources/{2}" />'.format(deck_id, cId, icard[1])
        card.add_resource(cId, icard[0],
                          os.path.join(os.path.dirname(os.path.abspath(__file__)),"deck_images",str(deck_id),icard[0])) # do this more gracefully
        card.add_resource(cId, icard[1],
                          os.path.join(os.path.dirname(os.path.abspath(__file__)),"deck_images",str(deck_id),icard[1])) # do this more gracefully
        card.update(cId, sideA, sideB)
        

    os.unlink(data['name'])        # let the filesystem delete the temp file
    return deck.get_json(dId)


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

