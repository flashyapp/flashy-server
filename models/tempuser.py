# User operations file

from flask import g
import bcrypt
from datetime import datetime

import user
from utils import id_generator

def exists_name(username):
    g.cur.execute("""
    SELECT COUNT(*)
    FROM tempusers
    WHERE username=%s""",
                  (username))
    
    ret, = g.cur.fetchone()

    if ret == 1:
        return True
    else:
        return False

def exists_email(email):
    g.cur.execute("""
    SELECT COUNT(*)
    FROM tempusers
    WHERE email=%s""",
                  (email))

    ret, = g.cur.fetchone()
    
    if ret == 1:
        return True
    else:
        return False

def new(username, email, password):
    # get the verification id's already used
    g.cur.execute("""
    SELECT verifyId
    FROM tempusers""")
    exist = [x[0] for x in g.cur.fetchall()]

    # create a new verification_id
    verify_id = id_generator(size=64, existing=exist)

    g.cur.execute("""
    INSERT INTO tempusers(verifyId, username, password, email, created)
    VALUES(%s, %s, %s, %s ,%s)""",
                  (verify_id,
                   username,
                   bcrypt.hashpw(password, bcrypt.gensalt()),
                   email,
                   datetime.now().isoformat()))
    g.db.commit()
    return verify_id

def verify(verify_id):
    g.cur.execute("""
    SELECT username, password, email
    FROM tempusers
    WHERE verifyId=%s""",
                  (verify_id))
    ret = g.cur.fetchone()
    if ret == None:
        return False            # there is no such verification Id
    username, password, email = ret
    delete(verify_id)
    return user.new(username, password, email)
    
def delete(verify_id):
    g.cur.execute("""
    DELETE FROM tempusers
    WHERE verifyId=%s""",
                  (verify_id))
    g.db.commit()
    if g.cur.rowcount == 1:
        return True
    else:
        return False


