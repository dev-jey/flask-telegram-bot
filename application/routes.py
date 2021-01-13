import time
import datetime
import threading
import re
import json
import os
import jwt
import random
import logging
from os import environ
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime as dt
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session, jsonify, abort
from flask import current_app as app
from flask_login import login_required, logout_user, current_user, login_user
from .factory import login_manager
from .models import db, User, Message
from .auth import sign_up
from .tasks import send_automated_messages
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from .messages import add_message, get_all_messages, edit_message
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from flask_login import login_required, current_user
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from flask import current_app as app
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from .telegram import TelegramFunctionality

options = webdriver.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-gpu')
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--headless")
options.add_argument("--disable-setuid-sandbox") 
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--disable-dev-shm-usage")
if os.environ.get('FLASK_ENV') == 'production':
    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
app.permanent_session_lifetime = datetime.timedelta(days=1)


logger = logging.getLogger(__name__)

telegramhelper = TelegramFunctionality()

# set log level
logging.basicConfig(level=logging.INFO,
                    format="\n\n{asctime:<12} '\n----------------------\n{levelname}: {message}\n----------------------\n' ({filename}:{lineno})\n\n", style="{")


'''
The automation
# '''


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
        data = get_all_messages(current_user)
        return render_template("messages.html", user=current_user, data=data )
    except BaseException as e:
        logger.error(f'An error occurred: {e}')
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
        logger.error(f'An error occurred: {e}')
        msg = f"The activation link is either broken or expired"
        return render_template("verified.html", msg=msg)


@app.route('/login', methods=['POST'])
def login():
    try:
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
                if not user.activated:
                    return make_response(f"We sent  an activation link to your email. Open it to continue", 400)
                user.authenticated = True
                db.session.commit()
                login_user(user, remember=True)
                return make_response(f'Login Successful', 200)
        return make_response(f'Wrong credentials! Try again', 403)
    except BaseException as e:
        logger.error(f'An error occurred: {e}')
        return make_response(f'We are experiencing some trouble logging you in. Please try again', 403)


@app.route('/logout', methods=["POST"])
@login_required
def logout():
    """Logout via query string parameters."""
    try:
        user = current_user
        user.authenticated = False
        db.session.commit()
        logout_user()
        return make_response(f'Logout successful', 200)
    except Exception as e:
        return make_response(f'We are having trouble logging you out. Try again later', 400)



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
    return add_message(name, message, duration, user)


@app.route("/edit/<message_id>", methods=['GET'])
@login_required
def open_edit_message(message_id):
    try:
        message_details = Message.query.filter(
            Message.id == message_id
        ).first()
        return render_template('editmessage.html', message_details=message_details)
    except BaseException as e:
        logger.error(f'An error occurred: {e}')
        return render_template('editmessage.html', message_details=None)


@app.route("/edit_message", methods=['POST'])
@login_required
def edit_a_message():
    data = request.get_json()
    id_ = data["id"]
    name = data['name']
    message = data['message']
    duration = data['duration']
    user = current_user
    return edit_message(name, message, duration, user, id_)


@app.route("/send_code", methods=['POST'])
@login_required
def send_code():
    global driver
    driver = telegramhelper.check_chrome_driver_path(options)
    wait = WebDriverWait(driver, 30)
    executor_url = driver.command_executor._url
    session_id = driver.session_id
    try:
        data = request.get_json()
        pid = data["pid"]
        code = data["code"]
        mobile_no = data["mobile"]
        process = Message.query.filter(
            Message.id == int(pid)
        ).first()
        process.session_id = session_id
        process.executor_url = executor_url
        db.session.commit()
    except BaseException as e:
        logger.error(f'An error occurred: {e}')
        close_driver(driver)
        return make_response(f"We are experiencing a problem identifying the process to run", 400)

    logger.info(f"EXECUTOR_URL: {executor_url}, SESSION_ID:{session_id}")
    if code == "" or code is None:
        close_driver(driver)
        return make_response(f"Enter a valid country code e.g 254", 400)
    if mobile_no == "" or mobile_no is None or len(mobile_no) < 6:
        close_driver(driver)
        return make_response(f"Enter a valid mobile no e.g 0712345678", 400)
    telegramhelper.try_to_login(wait, code, mobile_no, logger)
    # Wrong mobile number error
    if telegramhelper.check_if_multiple_sends(logger):
        return make_response(f"Code can't be sent. You are performing too many actions. Please try again later.", 400)
    if not telegramhelper.check_code_sent():
        return make_response(f"We are experiencing a problem sending the code", 400)
    return make_response(f"Code has been sent. Check your messages or telegram app", 200)


@app.route("/verify_code", methods=['POST'])
@login_required
def verify_mobile_code():
    data = request.get_json()
    my_code = data["my_code"]
    pid = data["pid"]
    telegramhelper.validate_verification_code(my_code)
    logger.info(f"My_code: {my_code} PID: {pid}")
    process = telegramhelper.get_current_process_from_db(pid)
    driver2 = telegramhelper.connect_to_existing_driver()

    if driver2.session_id != process.session_id:
        close_driver(driver2)
    driver2.session_id = process.session_id
    logger.info(f"SessionID {driver2.session_id}")
    wait = WebDriverWait(driver2, 30)
    try:
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@ng-model='credentials.phone_code']")))
        phone_input = driver2.find_element_by_xpath(
            "//input[@ng-model='credentials.phone_code']")
        phone_input.clear()
        phone_input.send_keys(my_code)
        wait.until(
            lambda driver: driver2.current_url == 'https://web.telegram.org/#/im')
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@ng-model='search.query']")))
        saved_message = Message.query.filter(
            Message.id == int(pid)
        ).first()
        driver2.find_element_by_xpath(
            "//input[@ng-model='search.query']").send_keys(saved_message.name)
        driver2.implicitly_wait(3)
        channel_search = telegramhelper.search_channel(logger)
        channel_detail = telegramhelper.check_channel_details(channel_search["search_results"], channel_search["search_results_alternate"], logger)
        return make_response(jsonify({
            "message": "Confirm channel details to proceed",
            "can_send": channel_detail["can_send"],
            "channel_name": channel_detail["channel_name"],
            "channel_members": channel_detail["channel_members"]
        }), 200)

    except BaseException as e:
        close_driver(driver2)
        logger.error(f'An error occurred: {e}')
        return make_response("We experienced a problem verifying your code.", 401)



'''
Close and Quit the current driver
'''


def close_driver(driver):
    driver.close()
    driver.quit()


'''
Start process
'''


@app.route("/start_process", methods=['POST'])
@login_required
def start_process():
    try:
        data = request.get_json()
        pid = data['pid']
        send_automated_messages.delay(pid)
        return make_response(f"Success. The process automation will start soon", 200)
    except BaseException as e:
        logger.info(f"An error occurred : {e}")
        return make_response(f"We are having trouble starting the process. Please try again later", 400)


'''
Stop Process
'''


@app.route('/stop_process', methods=['POST'])
def stop_process():
    try:
        data = request.get_json()
        pid = data["pid"]
        existing_process = Message.query.filter(
            Message.id == int(pid)
        ).first()
        driver4 = webdriver.Remote(
            command_executor=existing_process.executor_url, desired_capabilities=DesiredCapabilities.CHROME)
        if driver4.session_id != existing_process.session_id:
            close_driver(driver4)
        driver4.session_id = existing_process.session_id
        existing_process.on = False
        existing_process.session_id = None
        existing_process.executor_url = None
        db.session.commit()  # Commits all changes
        close_driver(driver4)
        return make_response("Messaging has been stopped", 200)
    except BaseException as e:
        logger.error(f'An error occurred: {e}')
        return make_response("We experienced a problem while stopping the messaging process", 400)


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


'''
Error logger helper
'''

