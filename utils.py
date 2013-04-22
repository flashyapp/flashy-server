import logging
from flask import request

def valid_params(params, data):
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
    

