# Deck operations file
from flask import g

def exists(dId):
    g.cur.execute("""
    SELECT EXISTS(SELECT * FROM decks WHERE id=%s)
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
    g.cur.execute("""
    DELETE from decks
    WHERE id=%s
    """, (dId))
    g.db.commit()
    return g.cur.rowcount

def modify(dId, name, desc):
    g.cur.execute("""
    UPDATE
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
    dId, = g.cur.fetchone()
    return dId

def get_json(dId):
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

def get_decks_by_uId(uId):
    g.cur.execute("""
    SELECT name, deck_id, description
    FROM decks
    WHERE creator=%s""", (uId))
    ret = g.cur.fetchall()
    return ret
