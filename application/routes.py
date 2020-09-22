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
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
from flask import current_app as app
from flask_login import login_required, logout_user, current_user, login_user
from .factory import login_manager
from .models import db, User, Message
from .auth import sign_up
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from .messages import add_message, get_all_messages, edit_message
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from flask_login import login_required, current_user
from selenium.webdriver.support import expected_conditions as EC
from flask import current_app as app
from .models import db, User, Message
from application import celery
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--incognito")
options.add_argument("--headless")
options.add_experimental_option("detach", True)
if os.environ.get('FLASK_ENV') == 'production':
    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
app.permanent_session_lifetime = datetime.timedelta(days=365)


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
    try:
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
    except BaseException as e:
        print("Error", e)
        return make_response(f'We are experiencing some trouble logging you in. Please try again', 403)



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
        print(e)
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
    try:
        data = request.get_json()
        code = data["code"]
        mobile_no = data["mobile"]
        global driver
        if os.environ.get('FLASK_ENV') == 'production':
            driver = webdriver.Chrome(executable_path=str(
                os.environ.get('CHROMEDRIVER_PATH')), options=options)
        else:
            driver = webdriver.Chrome(
                ChromeDriverManager().install(), options=options)
        wait = WebDriverWait(driver, 10000)

        executor_url = driver.command_executor._url
        session_id = driver.session_id

        session['session_id'] = session_id
        session['executor_url'] = executor_url
        print(executor_url, ">>>>><<<<<<<", session_id)
        if code == "" or code is None:
            return make_response(f"Enter a valid country code e.g 254", 400)
        if mobile_no == "" or mobile_no is None:
            return make_response(f"Enter a valid mobile no e.g 0712345678", 400)
        driver.get('https://web.telegram.org/#/login')
        wait.until(
            lambda driver: driver.current_url == 'https://web.telegram.org/#/login')
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input")))

        # Codefield
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input"
        ).send_keys(code)
        # MobileField
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
        ).send_keys(mobile_no)
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
        ).send_keys(Keys.ENTER)
        wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//button[@ng-click='$close(data)']"))
        )
        driver.find_element_by_xpath(
            "//button[@ng-click='$close(data)']").click()
        # Wrong mobile number error
        try:
            wrong_number = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//label[@my-i18n='login_incorrect_number']"))
            )
            if wrong_number:
                return make_response(f"Code can't be sent. You entered a wrong phone number format.", 400)
        except BaseException as e:
            print("1. Success, Mobile number correct")
        try:
            # Check for too many times error
            too_many_times = driver.find_element_by_xpath(
                "//button[@ng-click='$dismiss()'").is_displayed()
            if too_many_times:
                return make_response(f"Code can't be sent. You are performing too many actions. Please try again later.", 400)
        except BaseException as e:
            print("2. Success, No too many times error")
        print("3. ", "Success, Code has been Sent")
        return make_response(f"Code has been sent", 200)
    except BaseException as e:
        print("Error: ", e)
        return make_response(f"We are experiencing a problem sending the code", 400)


@app.route("/verify_code", methods=['POST'])
@login_required
def verify_mobile_code():
    try:
        data = request.get_json()
        my_code = data["my_code"]
        session_id = session.pop('session_id', None)
        executor_url = session.pop('executor_url', None)
        if my_code == "" or my_code is None:
            return make_response(f"Enter a verification code", 400)
        if len(my_code) != 5:
            return make_response(f"Code must be  5 digits.", 400)
        pid = data["pid"]
        print(my_code, pid, ">>>>>>>>>>>>>>>>>>>>>>>>>>")
        driver2 = webdriver.Remote(
            command_executor=executor_url, desired_capabilities={})
        if driver2.session_id != session_id: 
            driver2.close()   
            driver2.quit()  
        driver2.session_id = session_id
        print("SessionID", driver2.session_id )
        wait = WebDriverWait(driver2, 10000)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@ng-model='credentials.phone_code']")))
        driver2.find_element_by_xpath("//input[@ng-model='credentials.phone_code']").send_keys(my_code)
        try:
            wrong_code = WebDriverWait(driver2, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//label[@my-i18n='login_incorrect_sms_code']"))
            )
            if wrong_code:
                return make_response(f"Kindly enter the correct code.", 400)
        except BaseException as e:
            print(e, "Entered code is correct")
        wait.until(
            lambda driver: driver2.current_url == 'https://web.telegram.org/#/im')
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@ng-model='search.query']")))
        driver2.find_element_by_xpath("//input[@ng-model='search.query']").send_keys('Academic Writers')
        driver2.implicitly_wait(3)
        try:
            search_results = driver2.find_elements_by_xpath("//a[@ng-mousedown='dialogSelect(myResult.peerString)']")
            if len(search_results) == 0:
                return make_response(f"The given channel or group or username doesnot exist on your account.", 400)
        except BaseException as e:
            print(e, 'Search results found')

        driver2.find_elements_by_xpath("//a[@ng-mousedown='dialogSelect(myResult.peerString)']")[0].click()
        channel_name = driver2.find_element_by_xpath("//span[@my-peer-link='historyPeer.id']").text
        driver2.find_element_by_xpath("//span[@my-peer-link='historyPeer.id']").click()
        driver2.implicitly_wait(3)
        profile_img = None
        channel_members=None
        try:
            channel_members= driver2.find_element_by_xpath("//span[@my-chat-status='-historyPeer.id']").text
            profile_img = driver2.find_element_by_xpath("//img[@class='peer_modal_photo']").get_attribute("src")
        except:
            pass

        print("Channel Name: ", channel_name)
        print("Channel_members",channel_members)
        print("Profile_img_link", profile_img)

        driver2.find_element_by_xpath("//a[@ng-click='goToHistory()']").click()

        # process = Message.query.filter(
        #     Message.id == int(pid)
        # ).first()
        # driver2.get(process.link)
        return make_response(f"The messaging process will start soon.", 200)
    except BaseException as e:
        print("Error ", e)
        return make_response(f"We experienced a problem verifying your code.", 400)



# @celery.task(name="Send mobile verification code")
# def send_mobile_code(mobile_no, code):
#     try:
#         driver.get('https://web.telegram.org/#/login')
#         wait.until(
#             lambda driver: driver.current_url == 'https://web.telegram.org/#/login')
#         wait.until(
#             EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input")))
#         #Codefield
#         driver.find_element_by_xpath(
#             "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input"
#         ).send_keys(code)
#         #MobileField
#         driver.find_element_by_xpath(
#             "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
#         ).send_keys(mobile_no)
#         driver.find_element_by_xpath(
#             "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
#         ).send_keys(Keys.ENTER)
#         wait.until(
#             EC.visibility_of_element_located((By.XPATH, "//span[@ng-click='$close(data)']"))
#         )
#         driver.find_element_by_xpath("//span[@ng-click='$close(data)']").click()
#         #Wrong mobile number error
#         try:
#             wrong_number = WebDriverWait(driver, 10).until(
#                 EC.visibility_of_element_located((By.XPATH, "//label[@my-i18n='login_incorrect_number']"))
#             )
#             if wrong_number:
#                 return {"resp":"Code can't be sent. You entered a wrong phone number format.","status": 400}
#         except BaseException as e:
#             print("1. Success, Mobile number correct")
#         try:
#             #Check for too many times error
#             too_many_times = driver.find_element_by_xpath("/html/body/div[5]/div[2]/div/div/div[2]/button").is_displayed()
#             if too_many_times:
#                 return {"resp":"Code can't be sent. You are performing too many actions. Please try again later.", "status":400}
#         except BaseException as e:
#             print("2. Success, No too many times error")
#         print("3. ", "Success, Code has been Sent")
#         return {"resp":"Code has been sent", "status":200}

#     except BaseException as e:
#         print("Error: ", e)
#         return {"resp":"We are experiencing a problem sending the code", "status":400}


# @celery.task(name="Authorize verification code")
# def verify_code(my_code, pid):
#     try:
#         driver2 = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
#         driver2.session_id = session_id
#         print (driver2.current_url)
#         driver2.find_element_by_xpath(
#             "/html/body/div[1]/div/div[2]/div[2]/form/div[4]/input"
#         ).send_keys(my_code)
#         print(pid, my_code, ">>>>>>>>>>>>>>>>>")
#         wait.until(
#             lambda driver: driver2.current_url == 'https://web.telegram.org/#/im')
#         driver2.implicitly_wait(5)
#         process = Message.query.filter(
#             Message.id == int(pid)
#             ).first()
#         driver2.get(process.link)
    # wait.until(
    #     lambda driver: driver2.current_url == process.link)
    # if process.link == driver2.current_url:
    #     new_process = update_process(pid)
    #     iterations=0
    #     while True:
    #         time.sleep(random.randint(-9, 9) + int(new_process.duration)*int(environ.get('TIME_MEASURE_SECONDS')))
    #         textarea = driver2.find_element_by_xpath(
    #             "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]").send_keys(new_process.message)
    #         driver2.find_element_by_xpath(
    #             "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[3]/button").click()
    #         iterations += 1
    #         new_process.iterations = iterations
    #         db.session.commit()  # Commits all changes
    # else:
    #     driver2.close()
    #     return {"message":"Messaging Started", "status": 200}
    # except BaseException as e:
    #     print("Error: ",e)
    #     driver2.close()
    #     return {"message":"We are having trouble starting your messaging service. Try again later", "status": 400 }


@app.route('/stop')
def stop_process():
    try:
        pid = request.args.get("pid")
        existing_process = Message.query.filter(
            Message.id == int(pid)
        ).first()
        existing_process.on = False
        driver.close()
        return make_response("Stopped")
    except BaseException as e:
        print(e)


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
