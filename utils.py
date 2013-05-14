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

import logging
from flask import request
import string
import random

def valid_params(params, data):
    """Do the parameters exist for a given function call
    """
    if data == None:
        return False
        
    for param in params:
        if param not in data:
            logging.debug("Param: {0} missing!".format(param))
            return False

    return True
        
def log_request(req):
    logging.debug("""
--------------------------------------------------
{2}
--------------------------------------------------
    headers: {0}
    method: {1}
    path: {2}
    url: {3}
    is_xhr: {4}
    blueprint: {5}
    endpoint: {6}

    json: {7}
    form: {8}
    args: {9}
    cookies: {10}
    
    files: {11}""".format(
        req.headers,
        req.method,
        req.path,
        req.url,
        req.is_xhr,
        req.blueprint,
        req.endpoint,
        req.json,
        req.form.keys(),
        req.args.keys(),
        req.cookies,
        req.files.keys()))
    

def id_generator(size=6, chars=string.ascii_uppercase + string.digits, existing=set([])):
    """
    Generate a unique id number
    """
    while True:
        ret = ''.join(random.choice(chars) for x in range(size))
        if ret not in existing:
            return ret
    # TODO: add some failure code to ensure non infinite loop
    assert False, "Infinite loop broke in {0}".format(__name__)

def pairs(lst):
    if len(lst) % 2 == 1:
        lst.append(None)
    return zip(lst[::2], lst[1::2])




