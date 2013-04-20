## Card Operations
####################

def new(dId, sideA, sideB):
    """Create a new card in the database
    Creates a new card type in the 'cards' database
    This function is assumed to be called within a request context so the global
    variable `g` is available to it
    """
    # TODO implement hashing
    hashval = 0
    g.cur.execute("""
    INSERT INTO cards (deck, sidea, sideb, hash)
    VALUES(%s, %s, %s, %s)""", (dId, sideA, sideB, hashval))
    g.db.commit()
    return g.cur.lastrowid


def get_cId(dId, index):
    g.cur.execute("""
    SELECT id
    FROM cards
    WHERE dId=%s, card_id=%s""",
                  (dId, index))
    ret, = g.cur.fetchone()
    return ret
    
def update(cId, sideA, sideB):
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
    
def add_resource(cId, name, path):
    # TODO: get the resource's hash
    hashval = 0
    g.cur.execute("""
    INSERT INTO card_resouces(cId, name, path, hash)
    VALUES(%s, %s, %s, %s)
    """, (cId, name, path, hashval))
    g.db.commit()
    return g.cur.lastrowid

def get_resource(cId, name):
    cur.execute("""
    SELECT id, name, path, hash
    FROM card_resouces
    WHERE cID=%s, name=%s""", (cId))
    val = cur.fetchone()
    return val
    
def get_resources(cId):
    cur.execute("""
    SELECT id, name, path, hash
    FROM card_resouces
    WHERE cID=%s""", (cId))
    vals = cur.fetchall()
    return vals
    
