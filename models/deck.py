# Deck operations file
from flask import g
from utils import id_generator

import card, user

def exists(dId):
    g.cur.execute("""
    SELECT EXISTS(
      SELECT *
      FROM decks
      WHERE id=%s)
    """, dId)
    r, = g.cur.fetchone()
    return True if r == 1 else False

def new(deckname, uId, desc):
    """Create a new deck in the database
    Creates a new deck in the 'decks' database
    This function is assumed to be called within a request context so the global
    variable `g` is available to it
    """
    # generate a unique id
    # TODO: fix collisions
    deck_id = id_generator(size=16)
    g.cur.execute("""
    INSERT INTO decks (deck_id, name, creator, description, hash)
    VALUES(%s, %s, %s, %s, %s)
    """, (deck_id, deckname, uId, desc, 0)) # hash to be updated later
    g.db.commit()
    return (g.cur.lastrowid, deck_id)

def delete(dId):
    # get all the cards associated with the deck
    g.cur.execute("""
    SELECT id
    FROM cards
    WHERE deck=%s""",
                  (dId))
    ids = [x[0] for x in g.cur.fetchall()]
    # delete all the cards associated with the deck
    for cId in ids:
        card.delete(cId)

    # delete the deck
    g.cur.execute("""
    DELETE from decks
    WHERE id=%s
    """, (dId))
    g.db.commit()
    return g.cur.rowcount

def modify(dId, name, desc):
    g.cur.execute("""
    UPDATE decks
    SET name=%s, description=%s
    WHERE id=%s
    """, (name, desc, dId))
    g.db.commit()
    return g.cur.rowcount
    
def get_id(deck_id):
    g.cur.execute("""
    SELECT id
    FROM decks
    WHERE deck_id=%s""", (deck_id))
    ret = g.cur.fetchone()
    if ret == None:
        return -1
    else:
        return ret[0]

def get_deck(dId):
    """Get a deck in json format
    Retrieves the deck information and all associated cards and jsonifys them
    format defined by [TODO: insert the link to the formatting of the json format for deck]
    """
    ret = {}
    # get the deck information
    g.cur.execute("""
    SELECT name, creator, description, deck_id FROM decks WHERE id=%s
    """, dId)
    name, creator, desc, deck_id = g.cur.fetchone()
    ret['name'] = name
    ret['creator'] = user.get_username(creator)
    ret['description'] = desc
    ret['deck_id'] = deck_id
    
    g.cur.execute("""
    SELECT sidea, sideb, card_id FROM cards WHERE deck=%s
    """, int(dId))
    ret['cards'] = [{'index': c[2], 'sideA': c[0], 'sideB': c[1]} for c in g.cur.fetchall()]

    return ret
def get_owner(dId):
    """Get the deck's owner
    """
    g.cur.execute("""
    SELECT creator
    FROM decks
    WHERE id=%s""", (dId))
    g.cur.fetchone()

def is_owner(username, dId):
    """Check if the user owns the deck
    """
    uId = user.get_uId(username)
    if uId == -1:
        return False
    g.cur.execute("""
    SELECT COUNT(*)
    FROM decks
    WHERE id=%s AND creator=%s""", (dId, uId))
    ret = g.cur.fetchone()
    
    if ret == None:
        return False
    elif ret[0] == 1:
        return True
    else:
        return False
    
def get_decks_by_uId(uId):
    g.cur.execute("""
    SELECT name, deck_id, description
    FROM decks
    WHERE creator=%s""", (uId))
    ret = g.cur.fetchall()
    return ret
