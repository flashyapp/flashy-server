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
