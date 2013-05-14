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

# massive import list... might be indication this needs refactoring
import MySQLdb
import os
import json
import bcrypt
import string
import random
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime
from settings import PASSWORD

from flask import Blueprint, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

from models import user, tempuser
import logging
from utils import log_request

userops = Blueprint('userops', __name__)
MAX_SESSIONS=10

####################
## Helper functions
####################

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def send_email(addr, html, plaintext, subject):
    logging.debug("Sending email to {0}, subject: {1}\ncontents:\n{2}".format(addr, subject, html))
    user = "noreply.flashyapp@gmail.com"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = addr
    msg.attach(MIMEText(plaintext, 'plain'))
    msg.attach(MIMEText(html, 'html'))
    passwd = PASSWORD
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.login(user, passwd)
    smtpserver.sendmail(user, addr, msg.as_string())
    smtpserver.close()
    
def send_confirm_email(addr, verifystring):
    html = """
    <html>
    <head></head>
    <body>
    This is a verification email for flashyapp, to complete your registration please visit the following link
    <a href="http://flashyapp.com/api/user/verify/{0}">verify</a>

    <br />
    <br />

    If you have recieved this message in error, do not press the link above and ignore this message
    </body>
    </html>
    """.format(verifystring)
    plaintext = """
    Please visit http://flashyapp.com/api/user/verify/{0} to activate your account
    """.format(verifystring)
    send_email(addr, html, plaintext, "Flashy Registration")

def send_reset_email(addr, passwd):
    html = """
    <html>
    <head></head>
    <body>
    You have reset your password to Flashyapp.com, please login using the following temporary password<br />

    {0}    
    <br />
    <br />

    If you have recieved this message in error, do not press the link above and ignore this message
    </body>
    </html>
    """.format(passwd)
    plaintext = """
    Your new password is: {0}
    """.format(passwd)
    send_email(addr, html, plaintext, "Flashy - Reset Password")


####################
## Endpoints
####################

@userops.route('/create_user', methods=['POST'])
def create_user():
    log_request(request)
    if request.json == None:
        logging.debug("No json provided")
        return jsonify({'error': 10})

    # check parameters
    if 'username' not in request.json \
    or 'password' not in request.json \
    or 'email' not in request.json:
        logging.debug('Missing parameters')
        return jsonify({'error' : 500})
        
    username = request.json['username']
    password = request.json['password']
    email    = request.json['email']
    
    if username == None or password == None or email == None:
        logging.debug('Missing parameters')
        return jsonify({'error' : 500})
        
    ret = {'username_s' : 1, 'password_s' : 1, 'email_s' : 1}
    
    error = False               # was there an error creating the user
    username_count = 0
    
    # Check if the username is in use
    if user.exists_name(username) or tempuser.exists_name(username):
        ret['username_s'] = 0
        logging.debug("User already exists")
        error = True

    # Check if the email is already in use
    if user.exists_email(email) or tempuser.exists_email(email):
        ret['email_s'] = 0
        logging.debug("Email already in use")
        error = True

    # Assume for now that all passwords are valid
    # TODO: add password checking according to spec

    if error:
        return jsonify(ret)

    # Everything was successful add the user to tempusers and send an email to the enduser
    vId = tempuser.new(username, email, password)
    logging.debug("Succesfully added new temp user")
    send_confirm_email(email, vId)
    return jsonify(ret)
    
    
@userops.route('/verify/<vId>', methods=['GET'])
def verify(vId):
    log_request(request)
    # verify the user and create a new user

    redirect_to_index = redirect('/')
    response = current_app.make_response(redirect_to_index)
    
    if not tempuser.verify(vId):
        logging.debug("No such verification_id")
        return response
    logging.debug("user verified")
    return response
        
            
@userops.route('/modify', methods=['POST'])
def modify():
    log_request(request)
    username = request.json['username']
    oldpass = request.json['old_password']
    newpass = request.json['new_password']
    
        # create a fake session to validate the old password
    session_id = user.login(username, oldpass)
    if not user.verify(username, session_id):
        logging.debug("Invalid username or session_id")
        return jsonify({'error' : 101})
        
    user.logout(username, session_id)
        
    if user.modify(username, newpass):
        logging.debug("Modified user successfully")
        return jsonify({'error' : 0})
    else:
        logging.error("user modification returned failure!")
        return jsonify({'error' : -1}) # impossibru!!

@userops.route('/reset_password', methods=['POST'])
def reset_password():
    log_request(request)
    
    username = request.json['username']
    email = request.json['email']
    newpass = id_generator()

    if user.id_email(email) != user.id_name(username):
        logging.debug("Invalid username or session_id")
        return jsonify({'error' : 101})

    # Update the password to the temp password
    user.modify(username, newpass)
    # send the user the update password
    send_reset_email(email, newpass)

    return jsonify({'error' : 0})    
@userops.route('/login', methods = ['POST'])
def user_login():
    log_request(request)
    password = request.json['password']
    username = request.json['username']
    uId = user.get_uId(username)
    
    ret = {'error' : 0}
    
    if user.get_session_count(uId) >= MAX_SESSIONS:
        logging.debug("Too many sessions for {0}".format(username))
        ret['error'] = 103
    
    session_id = user.login(username, password)
    ret = {'error' : 0}
    if session_id == None:
        logging.debug("Invalid username or session_id")
        ret['error'] = 101
    else:
        logging.debug("Successfully logged in")
        ret['session_id'] = session_id

    return jsonify(ret)
    
@userops.route('/logout', methods=['POST'])
def user_logout():
    log_request(request)
    username = request.json['username']
    session_id = request.json['session_id']

    if user.logout(username, session_id):
        logging.debug("Logged out succesfully")
        return jsonify({'error' : 0})
    else:
        logging.debug("Invalid username or password")
        return jsonify({'error' : 101})

    
        
