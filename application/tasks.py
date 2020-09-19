import jwt
import os
from flask import current_app as app, render_template
from application import celery
from flask_mail import Mail, Message
from datetime import datetime, timedelta

mail = Mail(app)


@celery.task(name='Send Activation Email')
def send_activation_email(username, email):
    msg = Message('Telegram Textbot - Account verification required', sender = os.environ.get('MAIL_USERNAME'), recipients = [email])
    payload = {
        'email': email,
        'username': username,
        'exp': datetime.utcnow() + timedelta(minutes=60)
    }
    token = jwt.encode(payload, os.environ.get('SECRET_KEY'),
                        algorithm='HS256').decode('utf-8')
    link = os.environ.get('CURRENT_URL') + \
        f"verify/{token}"
    msg.html =  render_template('activation.html', title = 'Verify Your Account', username=username,link=link)
    mail.send(msg)