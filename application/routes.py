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
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask import current_app as app
from flask_login import login_required, logout_user, current_user, login_user
from .factory import login_manager
from .models import db, User, Message
from .auth import sign_up
from .messages import add_message, get_all_messages, edit_message, send_mobile_code



@login_manager.user_loader
def user_loader(user_email):
    """Given *user_email*, return the associated User object.

    :param unicode user_email: user_email (email) user to retrieve

    """
    return User.query.filter_by(email=user_email).first()



'''
All the Pages in the app
'''


@app.route('/')
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("index.html")



@app.route('/new')
@login_required
def new_process():
    return render_template("createmessage.html")


@app.route('/home', methods=['GET'])
@login_required
def home():
    try:
        messages = get_all_messages(current_user)
        return render_template("messages.html", user=current_user, messages=messages)
    except BaseException as e:
        print(e)
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
        if existing_user.activated:
            msg = f"User {username} already verified"
            return render_template("verified.html", msg=msg)
        existing_user.activated = True
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
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
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
        user.authenticated = True
        if check_password_hash(user.password, password):
            login_user(user, remember=True)
            return make_response(f'Login Successful', 200)
    return make_response(f'Wrong credentials! Try again', 403)


@app.route('/logout')
@login_required
def logout():
    """Logout via query string parameters."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for("welcome"))


'''
Messaging Functionality
'''

@app.route("/save_message", methods=['POST'])
@login_required
def save_message():
    data = request.get_json()
    name = data['name']
    message = data['message']
    duration = data['duration']
    user = current_user
    return add_message(name,message,duration, user)


@app.route("/edit/<message_id>", methods=['GET'])
@login_required
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
@login_required
def edit_a_message():
    data = request.get_json()
    id_= data["id"]
    name = data['name']
    message = data['message']
    duration = data['duration']
    user = current_user
    return edit_message(name,message,duration, user,id_)





@app.route("/send_code", methods=['POST'])
@login_required
def send_code():
    try:
        data = request.get_json()
        code = data["code"]
        mobile_no = data["mobile"]
        if not code:
            return make_response(f"Enter a valid country code e.g 254", 400)
        if not mobile_no:
            return make_response(f"Enter a valid mobile no e.g 0712345678", 400)
        resp = send_mobile_code.delay(mobile_no, code)
        print(resp)
        return make_response(f"We have sent a code to your phone.Check the telegram app or your messages", 200)
        
    except BaseException as e:
        print("Error: ", e)
        return make_response(f"We are experiencing a problem sending the code", 400)





@login_manager.user_loader
def load_user(user_email):
    """Check if user is logged-in on every page load."""
    if user_email is not None:
        return User.query.filter_by(email=user_email).first()
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('welcome'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
