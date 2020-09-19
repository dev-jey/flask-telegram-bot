import time
import datetime
import re
import json
import os
import jwt
import random
from os import environ
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime as dt
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session,jsonify
from flask import current_app as app
from .models import db, User, Message
from .auth import sign_up
from .messages import add_message, get_all_messages, edit_message



'''
All the Pages in the app
'''


@app.route('/')
def welcome():
    user = session.get('username')
    if user:
        return redirect(url_for("home"))
    return render_template("index.html")



@app.route('/new')
def new_process():
    user = session.get('username')
    if not user:
        return redirect(url_for("welcome"))
    return render_template("createmessage.html")


@app.route('/home', methods=['GET'])
def home():
    user = session.get('username')
    if not user:
        return redirect(url_for("welcome"))
    try:
        existing_user = User.query.filter(
            User.username == user
        ).first()
        messages = get_all_messages(existing_user)
        return render_template("messages.html", user=user, messages=messages)
    except BaseException as e:
        print(e)
        session.pop('username', None)
        return redirect(url_for("welcome"))



'''
User authentication views
'''


@app.route('/register', methods=['POST'])
def register():
    """Create a user via query string parameters."""
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    confirm_password = data['repassword']
    response = sign_up(username, email, password, confirm_password)
    return response



@app.route('/verify/<token>', methods=['GET'])
def activate_account(token):
    try:
        email = jwt.decode(token, os.environ.get('SECRET_KEY'))['email']
        existing_user = User.query.filter(
            User.email == email
        ).first()
        username = jwt.decode(token, os.environ.get('SECRET_KEY'))['username']
        msg = ""
        if existing_user.active:
            msg = f"User {username} already verified"
            return render_template("verified.html", msg=msg)
        existing_user.active = True
        db.session.commit()
        msg = f"Your account has been activated successfully"
        return render_template("verified.html", msg=msg, username=username)
    
    except BaseException as e:
        print(e)
        msg = f"The activation link is either broken or expired"
        return render_template("verified.html", msg=msg)



@app.route('/login', methods=['POST'])
def login():
    """Login via query string parameters."""
    data = request.get_json()
    user = data['email']
    password = data['password']
    if not user or not password:
        return make_response(f"Enter your username/email and password", 400)
    existing_username = None
    existing_email = None
    existing_email = User.query.filter(
        User.email == user).first()
    existing_username = User.query.filter(
        User.username == user).first()
    if existing_username or existing_email:
        user = existing_username or existing_email
        if check_password_hash(user.password, password):
            session['username'] = user.username
            return make_response(f'Login Successful', 200)
    return make_response(f'Wrong credentials! Try again', 403)


@app.route('/logout')
def logout():
    """Logout via query string parameters."""
    session.pop('username', None)
    return redirect(url_for("welcome"))


'''
Messaging Functionality
'''

@app.route("/save_message", methods=['POST'])
def save_message():
    data = request.get_json()
    name = data['name']
    message = data['message']
    duration = data['duration']
    user = session.get('username')
    return add_message(name,message,duration, user)


@app.route("/edit/<message_id>", methods=['GET'])
def open_edit_message(message_id):
    try:
        message_details =   Message.query.filter(
                Message.id == message_id
            ).first()
        return render_template('editmessage.html', message_details=message_details)
    except BaseException  as e:
        print(e)
        return render_template('editmessage.html', message_details=None)



@app.route("/edit_message", methods=['POST'])
def edit_a_message():
    data = request.get_json()
    id_= data["id"]
    name = data['name']
    message = data['message']
    duration = data['duration']
    user = session.get('username')
    return edit_message(name,message,duration, user,id_)



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
