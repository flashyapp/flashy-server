## Card Operations
####################
from flask import g
from utils import id_generator

import resource

def new(dId, sideA, sideB):
    """Create a new card in the database
    Creates a new card type in the 'cards' database
    This function is assumed to be called within a request context so the global
    variable `g` is available to it
    """
    g.cur.execute("""
    SELECT MAX(card_id)
    FROM cards
    WHERE deck=%s
    """, (dId))
    count = g.cur.fetchone()[0]
    if count == None:
        count = 1
    else:
        count +=1
    
    # TODO implement hashing
    hashval = 0
    g.cur.execute("""
    INSERT INTO cards (deck, sidea, sideb, hash, card_id)
    VALUES(%s, %s, %s, %s, %s)""", (dId, sideA, sideB, hashval, count))
    g.db.commit()
    return g.cur.lastrowid


def get_cId(dId, index):
    g.cur.execute("""
    SELECT id
    FROM cards
    WHERE dId=%s AND card_id=%s""",
                  (dId, index))
    ret, = g.cur.fetchone()
    return ret
    
def modify(cId, sideA, sideB):
    g.cur.execute("""
    UPDATE cards
    SET sideA=%s, sideB=%s
    WHERE id=%s""", (sideA, sideB, cId))
    return g.cur.rowcount

def delete(cId):
    g.cur.execute("""
    DELETE
    FROM cards
    WHERE id=%s""", (cId))
    g.db.commit()
    return g.cur.rowcount
    

    
