from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import datetime
import re
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime as dt
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import current_app as app
from .models import db, User


options = webdriver.ChromeOptions()


app.permanent_session_lifetime = datetime.timedelta(days=365)

@app.route('/')
def welcome():
    user = session.get('username')
    if user:
        return  redirect(url_for("home"))
    return render_template("index.html")

@app.route('/home')
def home():
    user = session.get('username')
    if user:
        return render_template("home.html", user=user)
    return redirect(url_for("welcome"))


@app.route('/register', methods=['GET'])
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
            paid=False,
            active=False,
            admin=False
        )
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
        return make_response(f"User successfully created! Login to continue")
    else:
        return make_response(f"A problem occurred during signup!")



@app.route('/login', methods=['GET'])
def login():
    """Login via query string parameters."""
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password:
        return make_response(f"Ensure all fields are filled!")
    existing_user = User.query.filter(
            User.email == user).first()
    existing_pass = User.query.filter(
         User.password == password
    ).first()
    if existing_user and existing_pass and check_password_hash(existing_user.password, password):
        session['username'] = existing_user.username
        return make_response(f'Login Successful')
    return make_response(f'Wrong credentials! Try again')

@app.route('/logout', methods=['GET'])
def logout():
    """Logout via query string parameters."""
    session.pop('username', None)
    return redirect(url_for("welcome"))



@app.route("/automate")
def start_messaging():
    link = request.args.get('link')
    message = request.args.get('msg')
    duration = request.args.get('duration')
    start_browser(link, message, duration)

def start_browser(link, message, duration):
    global driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    wait =  WebDriverWait(driver, 10000)
    driver.maximize_window()
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
        while True: 
            time.sleep(int(duration))
            textarea = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]").send_keys(message)
            driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[3]/button").click()
    else:
         driver.quit()


def close_windows():
    driver.close()
    driver.quit()
