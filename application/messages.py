from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import datetime as dt
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session,jsonify
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import current_app as app
from .models import db, User, Message
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
# options.binary_location = environ.get('GOOGLE_CHROME_BIN')
app.permanent_session_lifetime = dt.timedelta(days=365)


global driver
# driver = webdriver.Chrome(executable_path=str(environ.get('CHROMEDRIVER_PATH')), options=options)
# driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
# wait = WebDriverWait(driver, 10000)


'''
The automation
'''


def add_message(name,message,duration,user):
    try:
        invalidForm = validateAddForm(name, duration, message)
        if invalidForm:
            return invalidForm
        existing_user = User.query.filter(
            User.username == user
        ).first()
        new_process = Message(
            message=message,
            name=name,
            created=dt.datetime.now(),
            duration=duration,
            iterations=0,
            on=False,
            owner=existing_user.id
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
        existing_user = User.query.filter(
            User.username == user
        ).first()
        existing_message = Message.query.filter(
            Message.id == id_  and Message.owner ==  existing_user.id
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
        return make_response(f"Enter a channel or group or user name", 400)
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










@app.route("/automate", methods=['GET'])
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
        print(e)
        session.pop('username', None)
        return redirect(url_for("welcome"))
    return start_browser()


def start_browser():
    code = request.args.get('code')
    mobile_no = request.args.get('mobile_no')
    if not code:
        return make_response(f"Enter a valid country code e.g 254")
    if not mobile_no:
        return make_response(f"Enter a valid mobile no e.g 0712345678")
    try:
        driver.get('https://web.telegram.org/#/login')
        wait.until(
            lambda driver: driver.current_url == 'https://web.telegram.org/#/login')
        print(code, mobile_no)
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input")))
        code_field = driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input"
        ).send_keys(code)
        mobile_field = driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
        ).send_keys(mobile_no)
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
        ).send_keys(Keys.ENTER)
        wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[ng-click="$close(data)"]'))
        )
        driver.find_element_by_css_selector('button[ng-click="$close(data)"]').click()
        wait.until(
            EC.element_to_be_clickable((By.XPATH,  "/html/body/div[1]/div/div[2]/div[2]/form/div[4]/input")))
        return make_response(f"Code Has Been Sent")
    except BaseException as e:
        driver.close()
        driver.quit()
        print(e)
        return make_response(f"An Error occurred while sending the code")

@app.route("/verify", methods=['GET'])
def verify_code():
    try:
        my_code = request.args.get("my_code")
        if not my_code:
            return make_response(f"Enter a verification code")
        pid = request.args.get("pid")
        code_field = driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[4]/input"
        ).send_keys(my_code)
        wait.until(
            lambda driver: driver.current_url == 'https://web.telegram.org/#/im')
        driver.implicitly_wait(5)
        process = Process.query.filter(
            Process.id == int(pid)
            ).first()
        driver.get(process.link)
        wait.until(
            lambda driver: driver.current_url == process.link)
        if process.link == driver.current_url:
            new_process = update_process(pid)
            iterations=0
            while True:
                time.sleep(random.randint(-9, 9) + int(new_process.duration)*int(environ.get('TIME_MEASURE_SECONDS')))
                textarea = driver.find_element_by_xpath(
                    "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]").send_keys(new_process.message)
                driver.find_element_by_xpath(
                    "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[3]/button").click()
                iterations += 1
                new_process.iterations = iterations
                db.session.commit()  # Commits all changes
        else:
            driver.quit()
        return make_response(f"Process Started")
    except BaseException as e:
        print("Error: ",e)
        driver.close()
        driver.quit()
        return make_response(f"An error occured while starting process")




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
    existing_process.on = True
    db.session.commit()
    return existing_process





@app.route('/stop')
def stop_process():
    try:
        pid = request.args.get("pid")
        existing_process = Process.query.filter(
            Process.id == int(pid)
        ).first()
        existing_process.on = False
        driver.close()
        driver.quit()
        return make_response("Stopped")
    except BaseException as e:
        print(e)




@app.route('/processes', methods=['GET'])
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


