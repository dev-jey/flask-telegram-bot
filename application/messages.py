import datetime as dt
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask import current_app as app
from .models import db, User, Message
from application import celery
from flask_login import current_user


def add_message(name,message,duration,user):
    try:
        invalidForm = validateAddForm(name, duration, message)
        if invalidForm:
            return invalidForm
        new_process = Message(
            message=message,
            name=name,
            created=dt.datetime.now(),
            duration=duration,
            iterations=0,
            on=False,
            owner=current_user.id
        )
        db.session.add(new_process)  # Adds new Message record to database
        db.session.commit()  # Commits all changes
        return make_response(f"Message has been added successfully", 200)
    except Exception as e:
        print(e)
        return make_response(f"Message has not been added. Try again", 401)



def edit_message(name,message,duration,user,id_):
    try:
        invalidForm = validateAddForm(name, duration, message)
        if invalidForm:
            return invalidForm
        existing_message = Message.query.filter(
            Message.id == id_  and Message.owner ==  current_user.id
        ).first()
        existing_message.message=message,
        existing_message.name=name,
        existing_message.created=dt.datetime.now(),
        existing_message.duration=duration
        db.session.commit()  # Commits all changes
        return make_response(f"Message has been updated successfully", 200)
    except Exception as e:
        print(e)
        return make_response(f"Message has not been updated. Try again", 401)




def validateAddForm(name, duration, message):
    invalid = False
    if name == ""  or name is None:
        invalid = True
        return make_response(f"Enter a channel or group name", 400)
    if duration == ""  or duration is None:
        invalid = True
        return make_response(f"Enter a duration", 400)
    if message == ""  or message is None:
        invalid = True
        return make_response(f"Enter a message", 400)
    if int(duration) < 30:
        invalid = True
        return make_response(f"Duration (minutes) must be more than 30", 400)
    if int(duration) > 3600:
        invalid = True
        return make_response(f"Duration (minutes) must be less than 3600", 400)
    return invalid


'''
Get all Messages
'''
def get_all_messages(user):
    try:
        messages = Message.query.filter(
            Message.owner == user.id
        ).order_by(Message.created.desc()).all()
        return messages
    except BaseException as e:
        print(e)
        return []


'''
Helper functions
''' 
 