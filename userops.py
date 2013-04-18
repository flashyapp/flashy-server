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

####################
## Helper functions
####################

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def send_email(addr, html, plaintext, subject):
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

    

####################
## Endpoints
####################

@userops.route('/create_user', methods=['POST'])
def create_user():
    if request.json == None:
        return jsonify({'error': 10})
        
    username = request.json['username']
    password = request.json['password']
    email    = request.json['email']

    ret = {'username_s' : 1, 'password_s' : 1, 'email_s' : 1}
    error = False               # was there an error creating the user
    username_count = 0
    # Check if the user is in tempusers or users
    g.cur.execute("""
    SELECT COUNT(*) FROM tempusers WHERE username=%s""",
                  (username))
    username_count += g.cur.fetchone()[0]
    g.cur.execute("""
    SELECT COUNT(*) FROM users WHERE username=%s""",
                  (username))
    username_count += g.cur.fetchone()[0]

    if username_count != 0:
        ret['username_s'] = 0
        error = True

    # Check if the email is already in use
    email_count = 0
    g.cur.execute("""
    SELECT COUNT(*) FROM tempusers WHERE email=%s""",
                      (email))
    email_count += g.cur.fetchone()[0]
    g.cur.execute("""
    SELECT COUNT(*) FROM users WHERE email=%s""",
                      (email))
    email_count += g.cur.fetchone()[0]
        
    if email_count != 0:
        ret['email_s'] = 0
        error = True

    # Assume for now that all passwords are valid
    # TODO: add password checking according to spec

    if error:
        return jsonify(ret)

    # Everything was successful add the user to tempusers and send an email to the enduser
    vId = id_generator(size=64)
    g.cur.execute("""
    INSERT INTO tempusers (id, verifyId, username, password, email, created) VALUES(
     NULL, %s, %s, %s, %s, %s)""",
                  (vId,
                   username,
                   bcrypt.hashpw(password, bcrypt.gensalt()),
                   email,
                   datetime.now().isoformat()))
    g.db.commit()
    send_confirm_email(email, vId)
    return jsonify(ret)
    
    
@userops.route('/verify/<vId>', methods=['GET'])
def verify(vId):
    # check to see that the user is in the tempusers database
    g.cur.execute("""
    SELECT username, password, email FROM tempusers WHERE verifyId=%s""",
                  (vId))

    # check that there was a valid user
    result = g.cur.fetchone()
    if not result:
        # not found
        # TODO: log this
        return "Invalid verification id"
        
    username, password, email = result

    # add the new user to the users table
    g.cur.execute("""
    INSERT INTO users (username, password, email)
    VALUES(%s, %s, %s)
    """, (username, password, email))
    g.db.commit()
    
    # remove the user from the temp users
    g.cur.execute("""
    DELETE FROM tempusers WHERE username=%s
    """, (username))
    g.db.commit()
    # TODO: Log this
    return 'You are now verified!\n'

@userops.route('/modify', methods=['POST'])
def modify():
        username = request.json['username']
        oldpass = request.json['old_password']
        newpass = request.json['new_password']
        # check that the user exists
        g.cur.execute("""
        SELECT username, password from users WHERE username=%s""",
                      (username),
        )
        result = g.cur.fetchone()
        
        if not result:
            return jsonify({'error' : 101})

        username, hashed = result

        if bcrypt.hashpw(oldpass, hashed) != hashed:
            # bad password
            # TODO: log this
            return jsonify({'error' : 102})

        g.cur.execute("""
        UPDATE users
        SET password=%s
        WHERE username=%s""", (bcrypt.hashpw(newpass, bcrypt.gensalt()), username))
        g.db.commit()
        
        return jsonify({'error' : 0})

@userops.route('/reset_password')
def reset_password():
    username = request.json['username']
    email = request.json['email']
    newpass = id_generator()
    g.cur.execute("""
    UPDATE users
    SET password=%s
    WHERE username=%s AND email=%s
    """, (bcrypt.hashpw(newpass, bcrypt.gensalt()), username, email))
    try:
        g.db.commit()
        send_reset_email(email, newpass)
        return jsonify({'error' : 0})
    except MySQLdb.IntegrityError:
        return jsonify({'error' : 102})
        
    
@userops.route('/login', methods = ['POST'])
def user_login():
    password = request.json['password']
    username = request.json['username']
    print password
    g.cur.execute("""
    SELECT password, id FROM users WHERE username=%s
    """, (username))
    if g.cur.rowcount != 1:
        return 'No such user!'              # TODO: change to something more sane
        
    hashed, uId = g.cur.fetchone()
    if bcrypt.hashpw(password, hashed) == hashed:
        # return valid json object
        sId = id_generator(size=64)
        g.cur.execute("""
        INSERT INTO sessions (id, uId, lastactive)
        VALUES(%s, %s, %s)
        """, (sId, uId, datetime.now().isoformat()))
        return jsonify(session_id=sId)
    else:
        return jsonify({'error' : 101})

@userops.route('/logout', methods=['POST'])
def user_logout():
    username = request.json['username']
    sId = request.json['session_id']
    if not verify_session(username, sId):
        # invalid session
        return jsonify({'error' : 104})
        uId = get_uId(username)
        g.cur.execute("""
    DELETE FROM sessions
    WHERE uId=%s AND id =%s""", (uId, session_id))
        return jsonify({'error' : 0})
        
