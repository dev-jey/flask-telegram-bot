import re
import os
from werkzeug.security import generate_password_hash
from datetime import datetime as dt
from flask import make_response, render_template
from flask import current_app as app
from .models import User, db
from application.tasks import send_activation_email


'''
Signup functionality
'''
def sign_up(username, email, password, confirm_password):
    try:
        is_not_valid = validate(username, email, password, confirm_password)
        if is_not_valid:
            return is_not_valid
        already_existing = verify_existing(username, email)
        if already_existing:
            return already_existing
        password_hash = generate_password_hash(password)
        new_user = User(
            username=username.lower(),
            email=email.lower(),
            created=dt.now(),
            password=password_hash,
            activated=False,
            authenticated=False,
            paid=False,
            admin=False
        )
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
        return account_verification_email_send(username, email)
    except BaseException as e:
        print(e)
        return make_response(f"A problem occurred during signup", 400)


'''Signup Validations'''
def validate(username, email, password, confirm_password):
    resp = False
    username = username.lower()
    email = email.lower()
    if username == "" or  not username:
        resp = True
        return make_response("Enter a username", 400)
    if len(username) < 3:
        resp = True
        return make_response("Username is too short", 400)
    
    if len(username) > 15:
        resp = True
        return make_response("Username is too long", 400)

    if email == "" or  not email:
        resp = True
        return make_response("Enter an email", 400)
    EMAIL_REGEX = re.compile(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")
    if not EMAIL_REGEX.match(email):
        resp = True
        return make_response("Enter a valid email", 400)
    if password ==  "" or not password:
        resp = True
        return make_response("Enter a password", 400)
    if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
        resp = True
        return make_response("Enter a strong password", 400)
    if password != confirm_password:
        resp = True
        return make_response("Passwords do not match", 400)
    return resp


'''Check if username or email is already in use'''
def verify_existing(username, email):
    resp = False
    username = username.lower()
    email = email.lower()
    try:
        existing_username = User.query.filter(
            User.username == username
        ).first()

        existing_email = User.query.filter(
            User.email == email
        ).first()
        if existing_username:
            resp = True
            return make_response(f"Username already taken", 400)
        if existing_email:
            resp = True
            return make_response(f"Email already exists", 400)
    except BaseException as e:
        print(e)
    return resp


'''Send account verification email'''
def account_verification_email_send(username, email):
    try:
        send_activation_email.delay(username, email)
        return make_response(f"We've sent an email to {email}. Open it to activate your account. May take up to 5mins", 200)
    except BaseException as e:
        print("Email sending failed: ", e)
        return make_response(f"We experienced a problem sending an account activation email to you.", 400)
