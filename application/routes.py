from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import datetime
import re
from os import environ
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime as dt
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import current_app as app
from .models import db, User, Process



options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument('--disable-gpu')
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-setuid-sandbox") 
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--disable-dev-shm-usage")
app.permanent_session_lifetime = datetime.timedelta(days=365)


'''
All the Pages in the app
'''


@app.route('/')
def welcome():
    user = session.get('username')
    if user:
        return redirect(url_for("home"))
    return render_template("index.html")


@app.route('/home', methods=['POST', 'GET'])
def home():
    user = session.get('username')
    if not user:
        return redirect(url_for("welcome"))
    try:
        existing_user = User.query.filter(
            User.username == user
        ).first()
        if existing_user.admin:
            return redirect(url_for("admin"))
        return render_template("home.html", user=user, user_details=existing_user)
    except BaseException as e:
        session.pop('username', None)
        return redirect(url_for("welcome"))


@app.route('/admin')
def admin():
    user = session.get('username')
    try:
        existing_user = User.query.filter(
            User.username == user
        ).first()
        if not user:
            return redirect(url_for("welcome"))
        if not existing_user.admin:
            return redirect(url_for("home"))
        users = User.query.all()
        return render_template("admin.html", user=user, users=users)
    except BaseException as e:
        session.pop('username', None)
        return redirect(url_for("welcome"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


'''
User authentication views
'''


@app.route('/register', methods=['POST', 'GET'])
def register():
    """Create a user via query string parameters."""
    username = request.args.get('username')
    email = request.args.get('email')
    password = request.args.get('password')
    confirm_password = request.args.get('repassword')
    if not username or not email or not password:
        return make_response(f"Ensure all fields are filled!")
    EMAIL_REGEX = re.compile(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")
    if not EMAIL_REGEX.match(email):
        return make_response(f"Enter a valid email!")
    existing_user = User.query.filter(
        User.username == username or User.email == email
    ).first()

    if existing_user:
        return make_response(f'{username} ({email}) already created!')
    if password != confirm_password:
        return make_response(f"Passwords do not match!")
    if len(password) < 5:
        return make_response(f"Passwords must be longer than 5 characters!")

    password_hash = generate_password_hash(password)
    if username and email:
        new_user = User(
            username=username,
            email=email,
            created=dt.now(),
            password=password_hash,
            active=False,
            admin=False
        )
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
        return make_response(f"User successfully created! Login to continue")
    else:
        return make_response(f"A problem occurred during signup!")


@app.route('/login', methods=['POST', 'GET'])
def login():
    """Login via query string parameters."""
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password:
        return make_response(f"Ensure all fields are filled!")
    existing_user = User.query.filter(
        User.email == user).first()
    if existing_user and check_password_hash(existing_user.password, password):
        session['username'] = existing_user.username
        return make_response(f'Login Successful')
    return make_response(f'Wrong credentials! Try again')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Logout via query string parameters."""
    session.pop('username', None)
    return redirect(url_for("welcome"))


'''
The automation
'''


# @app.route("/automate", methods=['POST', 'GET'])
def start_messaging():
    user = session.get('username')
    try:
        existing_user = User.query.filter(
            User.username == user
        ).first()
        if not user:
            return redirect(url_for("welcome"))
        if existing_user.admin:
            return redirect(url_for("admin"))
    except BaseException as e:
        session.pop('username', None)
        return redirect(url_for("welcome"))
    pid = request.args.get('pid')
    link = request.args.get('link')
    message = request.args.get('msg')
    duration = request.args.get('duration')
    start_browser(pid, link, message, duration)


def start_browser(pid, link, message, duration):
    global driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    wait = WebDriverWait(driver, 10000)
    driver.maximize_window()
    try:
        driver.get('https://web.telegram.org/#/login')
        wait.until(
            lambda driver: driver.current_url == 'https://web.telegram.org/#/login')
        wait.until(
            lambda driver: driver.current_url == 'https://web.telegram.org/#/im')
        time.sleep(5)
        driver.get(link)
        wait.until(
            lambda driver: driver.current_url == link)
        if link == driver.current_url:
            new_process = None
            if pid:
                new_process = update_process(pid)
            else:
                new_process = save_process(message, link, duration)
            iterations = 0
            while True:
                time.sleep(int(duration)*int(environ.get('TIME_MEASURE_SECONDS')))
                textarea = driver.find_element_by_xpath(
                    "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]").send_keys(message)
                driver.find_element_by_xpath(
                    "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[3]/button").click()
                iterations += 1
                new_process.iterations = iterations
                db.session.commit()  # Commits all changes
        else:
            driver.quit()
    except BaseException as e:
        driver.close()
        driver.quit()

@app.route('/processes', methods=['POST', 'GET'])
def get_past_processes():
    user = session.get('username')
    if not user:
        return redirect(url_for("welcome"))
    try:
        existing_user = User.query.filter(
            User.username == user
        ).first()
        if existing_user.admin:
            return redirect(url_for("admin"))
        processes = Process.query.filter(
            Process.owner == existing_user.id
        ).all()
        return render_template('processes.html', user_details=existing_user, user=user, processes=processes)
    except BaseException as e:
        session.pop('username', None)
        return redirect(url_for("welcome"))



def save_process(message, link, duration):
    user = session.get('username')
    existing_user = User.query.filter(
        User.username == user
    ).first()
    new_process = Process(
        message=message,
        link=link,
        created=dt.now(),
        duration=duration,
        iterations=0,
        owner=existing_user.id
    )
    db.session.add(new_process)  # Adds new Process record to database
    db.session.commit()  # Commits all changes
    return new_process

def update_process(pid):
    user = session.get('username')
    existing_user = User.query.filter(
        User.username == user
    ).first()
    existing_process = Process.query.filter(
        Process.id == pid
    ).first()
    existing_process.created = dt.now()
    existing_process.iterations = 0
    db.session.commit()
    return existing_process

