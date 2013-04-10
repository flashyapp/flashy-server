import MySQLdb
import os
import md5

from flask import Blueprint, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from PIL import Image

from imageSplit import splitImage
from userops import verify_session, get_uId, get_username

deckops = Blueprint('deckops', __name__)

DECK_IMAGE_DIR = "deck_images"

def create_new_card(dId, sideA, sideB):
    m = md5.new()
    m.update(sideA)
    m.update(sideB)
    g.cur.execute("""
    INSERT INTO cards (deck, sidea, sideb, hash)
    VALUES(%s, %s, %s, %s)""", (dId, sideA, sideB, m.digest()))
    g.db.commit()

@deckops.route('/new/from_image', methods=['POST'])
def new_from_image():
    # Use the user post params and already uploaded photo to generate a deck from the post params
    data = request.json
    username = data['username']
    uId = get_uId(username)
    
    sId = data['session_id']
    if not verify_session(username, sId):
        print "failed to verify session"
        abort(400)              # TODO: do this more gracefully
        
    filename = data['name']
    if not filename or not os.path.exists(filename):
        abort(400)              # TODO: be more graceful like dancer or ox
        
    deckname = data['deck_name']
    desc = data['desc']
    # create the new deck in the database
    g.cur.execute("""
    INSERT INTO decks (name, creator, description, hash)
    VALUES(%s, %s, %s, %s)
    """, (deckname, uId,  desc, 0)) # hash will be updated later
    dId = g.cur.lastrowid

    # Create a directory to hold the deck images
    dirname = DECK_IMAGE_DIR + str(dId)
    os.mkdir(dirname)

    g.db.commit()
    # split the temp image
    i = Image.open(filename)
    imgs = splitImage(i, (data['vlines'], data['hlines']))

    # save the images in the deck file
    filelist = []
    for i, img in enumerate(imgs):
        filename = str(i) + ".jpg"
        filelist.append(filename)
        img.convert('RGB').save(os.path.join(dirname,filename))
        
    asides = filelist[:len(filelist)/2]
    bsides = filelist[len(filelist)/2:]
    for icard in zip(asides, bsides):
        sideA = '<img src="' + DECK_IMAGE_DIR + "/" + str(dId) + "/" + icard[0] + '" />'
        sideB = '<img src="' + DECK_IMAGE_DIR + "/" + str(dId) + "/" + icard[1] + '" />'
        create_new_card(dId, sideA, sideB)
        
    del i
    os.unlink(data['name'])        # let the filesystem delete the temp file
    return get_deck_json(dId)
    
def get_deck_json(dId):
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


@deckops.route('/get_deck/<dId>')
def get_deck(dId):
    return get_deck_json(dId)
