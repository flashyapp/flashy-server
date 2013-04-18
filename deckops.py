import MySQLdb
import os
import md5

from flask import Blueprint, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from PIL import Image

from imageSplit import splitImage
from userops import verify_session, get_uId, get_username

deckops = Blueprint('deckops', __name__, static_folder='deck_images')

"""
==============================
Helper functions
==============================
"""

def deck_exists(dId):
    g.cur.execute("""
    SELECT EXISTS(SELECT * FROM decks WHERE id=%s)
    """, dId)
    r, = g.cur.fetchone()
    return True if r == 1 else False
    
def create_new_card(dId, sideA, sideB):
    """Create a new card in the database
    Creates a new card type in the 'cards' database
    This function is assumed to be called within a request context so the global
    variable `g` is available to it
    """
    m = md5.new()
    m.update(sideA)
    m.update(sideB)
    g.cur.execute("""
    INSERT INTO cards (deck, sidea, sideb, hash)
    VALUES(%s, %s, %s, %s)""", (dId, sideA, sideB, m.digest()))
    g.db.commit()
    return g.cur.lastrowid

def create_new_deck(deckname, uId, desc):
    """Create a new deck in the database
    Creates a new deck in the 'decks' database
    This function is assumed to be called within a request context so the global
    variable `g` is available to it
    """
    g.cur.execute("""
    INSERT INTO decks (name, creator, description, hash)
    VALUES(%s, %s, %s, %s)
    """, (deckname, uId, desc, 0)) # hash to be updated later
    g.db.commit()
    return g.cur.lastrowid


def get_deck_json(dId):
    """Get a deck in json format
    Retrieves the deck information and all associated cards and jsonifys them
    format defined by [TODO: insert the link to the formatting of the json format for deck]
    """
    ret = {}
    # get the deck information
    g.cur.execute("""
    SELECT name, creator, description FROM decks WHERE id=%s
    """, dId)
    name, creator, desc = g.cur.fetchone()
    ret['name'] = name
    ret['creator'] = get_username(creator)
    ret['desc'] = desc
    
    g.cur.execute("""
    SELECT sidea, sideb FROM cards WHERE deck=%s
    """, int(dId))
    ret['cards'] = [{'sideA': c[0], 'sideB': c[1]} for c in g.cur.fetchall()]

    return jsonify(ret)


"""
==============================
Implemented Endpoints
==============================
"""
@deckops.route('/get_deck/<dId>')
def get_deck(dId):
    return get_deck_json(dId)

@deckops.route('/new/from_cards/', methods=['POST'])
def new_from_cards():
    data = request.json
    username = data['username']
    deckname = data['deck_name']
    desc     = data['desc']
    cards    = data['cards']
    sId      = data['session_id']
    
    # authenticate the user
    uId = get_uId(username)
    if not verify_session(username, sId):
        abort(400)

    # create the deck in the database
    dId = create_new_deck(deckname, uId, desc)

    # create the cards
    for card in cards:
        create_new_card(dId, card['sideA'], card['sideB'])

    return get_deck(dId)
    
@deckops.route('/new/from_image', methods=['POST'])
def new_from_image():
    # Use the user post params and already uploaded photo to generate a deck from the post params
    data = request.json
    username = data['username']
    uId = get_uId(username)
    
    sId = data['session_id']
    if not verify_session(username, sId):
        abort(400)              # TODO: do this more gracefully
        
    filename = data['name']
    if not filename or not os.path.exists(filename):
        abort(400)              # TODO: be more graceful like dancer or ox
        
    deckname = data['deck_name']
    desc = data['desc']
    # create the new deck in the database
    dId = create_new_deck(deckname, uId, desc)

    # Create a directory to hold the deck images
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
            os.path.join(os.path.dirname(os.path.abspath(__file__)),"deck_images",str(dId),filename))
        
    asides = filelist[:len(filelist)/2]
    bsides = filelist[len(filelist)/2:]
    for icard in zip(asides, bsides):
        sideA = '<img src="deck_images/' + str(dId) + "/" +  icard[0] + '"/ >'
        sideB = '<img src="deck_images/' + str(dId) + "/" +  icard[1] + '"/ >'
        create_new_card(dId, sideA, sideB)
        
    del i
    os.unlink(data['name'])        # let the filesystem delete the temp file
    return get_deck_json(dId)


@deckops.route('/modify/<dId>/add_cards')
def add_cards(dId):
    data = request.json
    username = data['username']
    deckname = data['deck_name']
    desc     = data['desc']
    cards    = data['cards']
    sId      = data['session_id']

    # authenticate the user
    if not verify_session(username, sId):
        abort(400)

    # check that the deck exists
    if not deck_exists(dId):
        abort(400)              # really need to find a better failure method

    for card in cards:
        create_new_card(dId, card['sideA'], card['sideB'])
        
    return get_deck_json(dId)

    
