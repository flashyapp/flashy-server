# The MIT License (MIT)

# Copyright (c) 2013 Flashy

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Nick Beaulieu"
__copyright__ = "Copyright 2013, Flashyapp"
__credits__ = ["Nick Beaulieu", "Joe Turchiano", "Adam Yabroudi"]
__license__ = "MIT"
__maintainer__ = "Nick Beaulieu"
__email__ = "nsbeauli@princeton.edu"
__status__ = "Production"
__date__ = "Mon May 13 19:50:55 EDT 2013"
__version__ = "1.0"


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
    """Get the card id given the deck id and its index
    SHOULD BE UNIQUE!!
    """
    g.cur.execute("""
    SELECT id
    FROM cards
    WHERE deck=%s AND card_id=%s""",
                  (dId, index))
    ret, = g.cur.fetchone()
    return ret
    
def modify(cId, sideA, sideB):
    """Modify an existing card
    """
    g.cur.execute("""
    UPDATE cards
    SET sideA=%s, sideB=%s
    WHERE id=%s""", (sideA, sideB, cId))
    return g.cur.rowcount

def delete(cId):
    """Delete a card given by the card id number"""
    g.cur.execute("""
    DELETE
    FROM cards
    WHERE id=%s""", (cId))
    g.db.commit()
    return g.cur.rowcount
    
def get_resources(cId):
    """Get the list of resources associated with the card"""
    g.cur.execute("""
    SELECT resource_id, name, path, hash
    FROM resources
    WHERE cID=%s""", (cId))
    vals = g.cur.fetchall()
    return vals
