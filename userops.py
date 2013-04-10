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
userops = Blueprint('userops', __name__)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
    
@userops.route('/new_user', methods=['POST'])
def new_user():
    data = request.json
    # TODO: check if the username already exists
    cur = g.db.cursor()
    vId = id_generator(size=64)
    cur.execute("""
    INSERT INTO tempusers (id, verifyId, username, password, email, created) VALUES(
     NULL, %s, %s, %s, %s, %s)""",
                (vId,
                 str(data['username']),
                 bcrypt.hashpw(str(data['password']), bcrypt.gensalt()),
                 str(data['email']),
                 datetime.now().isoformat()))
    send_confirm_email(data['email'], vId)
    return 'An email has been sent to {0}, please follow the instructions to activate your account\n'.format(data['email'])

def send_confirm_email(addr, verifystring):
    html = """
    <html>
    <head></head>
    <body>
    This is a verification email for flashyapp, to complete your registration please visit the following link
    <a href="http://flashyapp.com/api/user/verify_user/{0}">verify</a>

    <br />
    <br />

    If you have recieved this message in error, do not press the link above and ignore this message
    </body>
    </html>
    """.format(verifystring)
    plaintext = """
    Please visit http://flashyapp.com/api/user/verify_user/{0} to activate your account
    """.format(verifystring)
    
    user = "noreply.flashyapp@gmail.com"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your Registration for Flashyapp"
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
    
    
@userops.route('/verify_user/<Vid>', methods=['GET'])
def verify_user(Vid):
    # check to see that the user is in the tempusers database
    cur = g.db.cursor()
    cur.execute("""
    SELECT username, password, email FROM tempusers WHERE verifyId=%s""",
                (Vid))
    username, password, email = cur.fetchone()
    cur.execute("""
    INSERT INTO users (username, password, email)
    VALUES(%s, %s, %s)
    """, (username, password, email))
    g.db.commit()
    cur.execute("""
    DELETE FROM tempusers WHERE username=%s
    """, (username))
    return 'You are now verified!\n'

@userops.route('/login/<username>', methods = ['POST'])
def user_login(username):
    password = request.json['password']
    cur = g.db.cursor()
    cur.execute("""
    SELECT password, id FROM users WHERE username=%s
    """, (username))
    hashed, uId = cur.fetchone()
    if bcrypt.hashpw(password, hashed) == hashed:
        # return valid json object
        sId = id_generator(size=64)
        cur.execute("""
        INSERT INTO sessions (id, uId, lastactive)
        VALUES(%s, %s, %s)
        """, (sId, uId, datetime.now().isoformat()))
        return jsonify(session_id=sId)
        
    else:
        abort(401)              # TODO: change to a more sane option later
        
def get_uId(username):
    # get the userId associated with the username
    g.cur.execute("""
    SELECT id FROM users WHERE (username=%s)
    """, username)
    uId = g.cur.fetchone()[0]
    return uId

def get_username(uId):
    g.cur.execute("""
    SELECT username FROM users WHERE (id=%s)
    """, uId)
    username = g.cur.fetchone()[0]
    return username
    
def verify_session(username, sId):
    uId = get_uId(username)
    # if there is no user named `username`
    if uId == None:
        return False
    g.cur.execute("""
    SELECT * FROM sessions WHERE (id=%s  AND uId=%s)
    """, (sId, uId))
    sId, uId, lastactive = g.cur.fetchone()
    # No such session
    if lastactive == None:
        print "lastactive not set:" +  lastactive
        return False
    else:
        return True

    return False
        
