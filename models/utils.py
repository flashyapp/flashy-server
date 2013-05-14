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

import string
import random

# Adapted from response at
# http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
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
