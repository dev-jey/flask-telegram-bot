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
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session, jsonify
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
from flask import current_app as app
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

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
        error_logger(e)
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
        error_logger(e)
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
        error_logger(e)
        return make_response(f'We are experiencing some trouble logging you in. Please try again', 403)


@app.route('/logout', methods=["POST"])
@login_required
def logout():
    """Logout via query string parameters."""
    try:
        user = current_user
        user.authenticated = False
        db.session.add(user)
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
        error_logger(e)
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
    try:
        if os.environ.get('FLASK_ENV') == 'production':
            driver = webdriver.Chrome(executable_path=str(
                os.environ.get('CHROMEDRIVER_PATH')), options=options)
        else:
            driver = webdriver.Chrome(
                ChromeDriverManager().install(), options=options)
    except Exception as e:
        print(e)
        return make_response(f"We are having trouble processing your request. Please check your internet connection", 400)
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
        logger.info(f"EXECUTOR_URL: {executor_url}, SESSION_ID:{session_id}")
        if code == "" or code is None:
            close_driver(driver)
            return make_response(f"Enter a valid country code e.g 254", 400)
        if mobile_no == "" or mobile_no is None:
            close_driver(driver)
            return make_response(f"Enter a valid mobile no e.g 0712345678", 400)
        driver.get('https://web.telegram.org/#/login')
        wait.until(
            lambda driver: driver.current_url == 'https://web.telegram.org/#/login')
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input")))
        # Codefield
        code_field = driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input"
        )
        code_field.clear()
        code_field.send_keys(code)
        # MobileField
        mobile_field = driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
        )
        mobile_field.clear()
        mobile_field.send_keys(mobile_no)
        driver.implicitly_wait(3)
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
        ).send_keys(Keys.ENTER)
        try:
            wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//button[@ng-click='$close(data)']"))
            )
            driver.find_element_by_xpath(
                "//button[@ng-click='$close(data)']").click()
        except:
            close_driver(driver)
            error_logger(e)
            return make_response(f"We are experiencing a problem sending the code", 400)
        # Wrong mobile number error
        try:
            logger.info(f"Mobile no: {mobile_no}")
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//label[@my-i18n='login_incorrect_number']"))
            )
            if driver.find_element_by_xpath("//label[@my-i18n='login_incorrect_number']").is_displayed():
                print("WRONG NUMBER ", driver.find_element_by_xpath("//label[@my-i18n='login_incorrect_number']"))
                close_driver(driver)
                return make_response(f"Code can't be sent. You entered a wrong phone number format.", 400)
        except BaseException as e:
            logger.info("1. Success, Mobile number correct")
        try:
            # Check for too many times error
            too_many_times = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//button[@ng-click='$dismiss()']")))
            if too_many_times:
                close_driver(driver)
                return make_response(f"Code can't be sent. You are performing too many actions. Please try again later.", 400)
        except BaseException as e:
            logger.info("2. Success, No too many times error")
        try:
            driver.find_element_by_xpath("//input[@ng-model='credentials.phone_code']").is_displayed()
        except:
            return make_response(f"We are experiencing a problem sending the code", 400)
        return make_response(f"Code has been sent. Check your messages or telegram app", 200)
    except BaseException as e:
        error_logger(e)
        close_driver(driver)
        return make_response(f"We are experiencing a problem sending the code", 400)


@app.route("/verify_code", methods=['POST'])
@login_required
def verify_mobile_code():
    data = request.get_json()
    my_code = data["my_code"]
    pid = data["pid"]
    if my_code == "" or my_code is None:
        return make_response(f"Enter a verification code", 400)
    if len(my_code) != 5:
        return make_response(f"Code must be  5 digits.", 400)
    logger.info(f"My_code: {my_code} PID: {pid}")
    try:
        process = Message.query.filter(
            Message.id == int(pid)
        ).first()
    except:
        return make_response(f"We are having trouble processing your request.", 400)

    try:
        driver2 = webdriver.Remote(
            command_executor=process.executor_url, desired_capabilities={})
    except Exception as e:
        return make_response(f"We are having trouble processing your request. Please check your internet connection", 400)

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
        try:
            wrong_code = WebDriverWait(driver2, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//label[@my-i18n='login_incorrect_sms_code']"))
            )
            if wrong_code:
                return make_response(f"Kindly enter the correct code.", 400)
        except BaseException as e:
            logger.info("Entered code is correct")
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
        try:
            search_results = driver2.find_elements_by_xpath(
                "//a[@ng-mousedown='dialogSelect(myResult.peerString)']")
            search_results_alternate = driver2.find_elements_by_xpath(
                "//a[@ng-mousedown='dialogSelect(dialogMessage.peerString, dialogMessage.unreadCount == -1 && dialogMessage.mid)']"
            )
            if len(search_results) == 0 and len(search_results_alternate) == 0:
                close_driver(driver2)
                return make_response("The channel or group name was not found", 404)
        except BaseException as e:
            logger.info('Search results found')
        if search_results:
            driver2.find_elements_by_xpath(
                "//a[@ng-mousedown='dialogSelect(myResult.peerString)']")[0].click()
        if search_results_alternate:
            driver2.find_elements_by_xpath(
                "//a[@ng-mousedown='dialogSelect(dialogMessage.peerString, dialogMessage.unreadCount == -1 && dialogMessage.mid)']")[0].click()
        channel_name = driver2.find_element_by_xpath(
            "//span[@my-peer-link='historyPeer.id']").text
        channel_members = None
        can_send = None
        try:
            channel_members = driver2.find_element_by_xpath(
                "//span[@my-chat-status='-historyPeer.id']").text
            can_send = driver2.find_element_by_xpath(
                    "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]").is_displayed()
        except:
            pass

        logger.info(f"Channel Name: {channel_name}")
        logger.info(f"Channel_members: {channel_members}")
        logger.info(f"Can Send: {can_send}")
        payload = {
            "pid": pid,
            "can_send": can_send,
            "channel_name": channel_name,
            "channel_members": channel_members
        }
        token = jwt.encode(payload, os.environ.get('SECRET_KEY'),
                           algorithm='HS256').decode('utf-8')
        return make_response(jsonify({
            "message": "Confirm channel details to proceed",
            "token": token
        }), 200)

    except BaseException as e:
        close_driver(driver2)
        error_logger(e)
        return make_response("We experienced a problem verifying your code.", 401)


'''
Channel/Group/Name Details
'''


@app.route("/confirm_details", methods=['GET'])
@login_required
def confirm_channel_details():
    token = None
    payload = None
    pid = None
    channel_name = None
    channel_members = None
    try:
        token = request.args.get('token', None)
        payload = jwt.decode(token, os.environ.get('SECRET_KEY'))
        pid = payload['pid']
        can_send = payload['can_send']
        channel_name = payload['channel_name']
        channel_members = payload['channel_members']
    except BaseException as e:
        logger.info(f"Error {e}")
        return render_template("confirmdetails.html",
                               pid=pid, channel_name=channel_name,
                               can_send=can_send,
                               channel_members=channel_members
                               )
    return render_template("confirmdetails.html",
                           pid=pid, channel_name=channel_name,
                           can_send=can_send,
                           channel_members=channel_members
                           )


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
            command_executor=existing_process.executor_url, desired_capabilities={})
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
        error_logger(e)
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


def error_logger(e):
    return logger.error(f'An error occurred: {e}')
