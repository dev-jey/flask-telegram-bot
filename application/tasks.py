import jwt
import os
import time
import random
from datetime import datetime as dt
from flask import current_app as app, render_template, make_response
from flask_login import current_user
from application import celery
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from .models import db, Message


mail = Mail(app)


@celery.task(name='Send Activation Email')
def send_activation_email(username, email):
    msg = Message('Telegram Textbot - Account verification required',
                  sender=os.environ.get('MAIL_USERNAME'), recipients=[email])
    payload = {
        'email': email.lower(),
        'username': username.lower(),
        'exp': datetime.utcnow() + timedelta(minutes=60)
    }
    token = jwt.encode(payload, os.environ.get('SECRET_KEY'),
                       algorithm='HS256').decode('utf-8')
    link = os.environ.get('CURRENT_URL') + \
        f"verify/{token}"
    msg.html = render_template(
        'activation.html', title='Verify Your Account', username=username, link=link)
    mail.send(msg)


@celery.task(name='Send automated messages')
def send_automated_messages(pid):
    process = Message.query.filter(
        Message.id == int(pid) and Message.owner == current_user.id
    ).first()
    session_id = process.session_id
    executor_url = process.executor_url
    if not session_id or not executor_url:
        return make_response(f"You are currently not authenticated on telegram", 400)
    driver3 = webdriver.Remote(
            command_executor=executor_url, desired_capabilities={})
    if driver3.session_id != session_id:
        driver3.close()
        driver3.quit()
    driver3.session_id = session_id
    new_process = Message.query.filter(
        Message.id == int(pid)
    ).first()
    iterations = new_process.iterations or 0
    while True:
        time.sleep(random.randint(-1, 1) + int(new_process.duration)
                   * int(os.environ.get('TIME_MEASURE_SECONDS')))
        driver3.find_element_by_xpath(
            "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]").send_keys(new_process.message)
        driver3.find_element_by_xpath(
            "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]").send_keys(Keys.ENTER)
        iterations += 1
        new_process.created = dt.now()
        new_process.iterations = iterations
        new_process.on = True
        db.session.commit()  # Commits all changes
