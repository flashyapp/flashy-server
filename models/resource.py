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

from flask import g, current_app
from utils import id_generator
import os

def exists(rId):
    g.cur.execute("""
    SELECT EXISTS(
      SELECT *
      FROM resources
      WHERE id=%s)
    """, rId)
    r = g.cur.fetchone()
    return True if r == 1 else False
    
def new(f, filename, cId):
    # get existing resource ids & generate the id
    g.cur.execute("""
    SELECT resource_id
    FROM resources
    """)
    existing = ['00000000'] + [x[0] for x in g.cur.fetchall()]
    resource_id = id_generator(size=8, existing=existing)
    
    # save the file into the resource directory
    ext = os.path.splitext(filename)[1]
    dest = os.path.join(current_app.config['RESOURCE_DIRECTORY'], resource_id + ext)
    outfile = open(dest, mode="w")
    outfile.write(f.read())
    # add the resource to the resources table
    g.cur.execute("""
    INSERT
    INTO resources(cId, resource_id, name, path, hash)
    VALUES(%s, %s, %s, %s)""", (cId, resource_id, filename, "http://www.flashyapp.com/resources/" + resource_id + ext, 0))
    g.db.commit()
    return (g.cur.lastrowid, resource_id)

def delete(rId):
    g.cur.execute("""
    DELETE
    FROM resources
    WHERE id=%s""", rId)
    return g.cur.rowcount

    
    
