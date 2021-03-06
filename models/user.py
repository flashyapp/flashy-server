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

# User operations file

from flask import g

from utils import id_generator
from datetime import datetime
import bcrypt


def exists_name(username):
    g.cur.execute("""
    SELECT COUNT(*)
    FROM users
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
    FROM users
    WHERE email=%s""",
                  (email))
    ret, = g.cur.fetchone()

    if ret == 1:
        return True
    else:
        return False
        
def id_email(email):
    g.cur.execute("""
    SELECT id
    FROM users
    WHERE email=%s""",
                  (email))
    ret, = g.cur.fetchone()
    return ret
    
def id_name(username):
    g.cur.execute("""
    SELECT id
    FROM users
    WHERE username=%s""",
                  (username))
    ret =  g.cur.fetchone()
    if ret == None:
        return -1
    else:
        return ret[0]
    
def new(username, password, email):
    g.cur.execute("""
    INSERT INTO users(username, password, email)
    VALUES(%s, %s, %s)
    """, (username, password, email))
    g.db.commit()
    if g.cur.rowcount != 1:
        return False
    else:
        return True

def delete(username):
    g.cur.execute("""
    DELETE FROM users
    WHERE username=%s""",
                  (username))
    g.db.commit()
    if g.cur.rowcount != 1:
        return False
    else:
        return True

def modify(username, password):
    g.cur.execute("""
    UPDATE users
    SET password=%s
    WHERE username=%s""",
                  (bcrypt.hashpw(password, bcrypt.gensalt()),
                   username))
    g.db.commit()
    if g.cur.rowcount != 1:
        return False
    else:
        return True

def login(username, password):
    g.cur.execute("""
    SELECT id, password
    FROM users
    WHERE username=%s""",
                  (username))
    
    result = g.cur.fetchone()
    if result == None:
        return None;

    uId, hashed = result

    if bcrypt.hashpw(password, hashed) != hashed:
        return None;

    # Get existing session ids
    g.cur.execute("""
    SELECT id
    FROM sessions
    WHERE uId=%s""",
                  (uId))
    res = [x[0] for x in g.cur.fetchall()]

    # Create a new session id
    sId = id_generator(size=64, existing=set(res))

    g.cur.execute("""
    INSERT INTO sessions(id, uId, lastactive)
    VALUES(%s, %s, %s)""",
                  (sId,
                   uId,
                   datetime.now().isoformat()))
    g.db.commit()
    
    return sId
    
    
def logout(username, session_id):
    # get the user id
    uId = get_uId(username)
    if uId < 0:
        return False;
        
    g.cur.execute("""
    DELETE FROM sessions
    WHERE uId=%s
      AND id=%s""",
                  (uId, session_id))
    g.db.commit()
    if g.cur.rowcount == 1:
        return True
    elif g.cur.rowcount > 1:
        assert False, "More than one row affected by logout!"
    else:
        return False

def verify(username, session_id):
    # get the user Id
    uId = get_uId(username)
    if uId < 0:
        return False            # no such user

    g.cur.execute("""
    SELECT COUNT(*)
    FROM sessions
    WHERE id=%s
      AND uId=%s""",
                  (session_id, uId))
    res, = g.cur.fetchone()

    if res == 1:
        return True
    elif res > 1:
        assert False, "verification found two matching sessions!\n session table corrupted!"
    else:
        return False

def get_uId(username):
    g.cur.execute("""
    SELECT id
    FROM users
    WHERE username=%s""",
                  (username))
    res = g.cur.fetchone()

    if res == None:
        return -1
    else:
        return res[0]

def get_username(uId):
    g.cur.execute("""
    SELECT username
    FROM users
    WHERE id=%s""",
                  (uId))
    res, = g.cur.fetchone()

    return res

def get_session_count(uId):
    g.cur.execute("""
    SELECT COUNT(*)
    FROM sessions
    WHERE uId=%s""", (uId))
    return g.cur.fetchone()[0]
        
