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


