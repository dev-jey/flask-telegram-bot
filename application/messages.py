import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import datetime as dt
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
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
options.add_argument("--headless")
options.add_experimental_option("detach", True)
if os.environ.get('FLASK_ENV') == 'production':
    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
app.permanent_session_lifetime = dt.timedelta(days=365)






'''
The automation
'''

def start_browser():
    global driver
    if os.environ.get('FLASK_ENV') == 'production':
        driver = webdriver.Chrome(executable_path=str(os.environ.get('CHROMEDRIVER_PATH')), options=options)
    else:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    wait = WebDriverWait(driver, 10000)
    return wait, driver


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



@celery.task(name="Send mobile verification code")
def send_mobile_code(mobile_no, code):
    try:
        global driver
        if os.environ.get('FLASK_ENV') == 'production':
            driver = webdriver.Chrome(executable_path=str(os.environ.get('CHROMEDRIVER_PATH')), options=options)
        else:
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        wait = WebDriverWait(driver, 10000)
        driver.get('https://web.telegram.org/#/login')
        wait.until(
            lambda driver: driver.current_url == 'https://web.telegram.org/#/login')
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input")))
        #Codefield
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input"
        ).send_keys(code)
        #MobileField
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
        ).send_keys(mobile_no)
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
        ).send_keys(Keys.ENTER)

        wait.until(
            EC.visibility_of_element_located((By.XPATH, "//span[@my-i18n='modal_ok']"))
        )
        driver.find_element_by_xpath("//span[@my-i18n='modal_ok']").click()
        #Wrong mobile number error
        try:
            wrong_number = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//label[@my-i18n='login_incorrect_number']"))
            )
            if wrong_number:
                return {"resp":"Code can't be sent. You entered a wrong phone number format.","status": 400}
        except BaseException as e:
            print("1. Success, Mobile number correct")
        try:
            #Check for too many times error
            too_many_times = driver.find_element_by_xpath("/html/body/div[5]/div[2]/div/div/div[2]/button").is_displayed()
            if too_many_times:
                return {"resp":"Code can't be sent. You are performing too many actions. Please try again later.", "status":400}
        except BaseException as e:
            print("2. Success, No too many times error")
        print("3. ", "Success, Code has been Sent")
        return {"resp":"Code has been sent", "status":200}
    
    except BaseException as e:
        print("Error: ", e)
        return {"resp":"We are experiencing a problem sending the code", "status":400}

    


















@app.route("/verify", methods=['GET'])
def verify_code():
    try:
        wait, driver = start_browser()
        my_code = request.args.get("my_code")
        if not my_code:
            return make_response(f"Enter a verification code")
        pid = request.args.get("pid")
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[4]/input"
        ).send_keys(my_code)
        wait.until(
            lambda driver: driver.current_url == 'https://web.telegram.org/#/im')
        driver.implicitly_wait(5)
        process = Message.query.filter(
            Message.id == int(pid)
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
            driver.close()
        return make_response(f"Messaging Started")
    except BaseException as e:
        print("Error: ",e)
        driver.close()
        return make_response(f"An error occured while starting process")





@app.route('/stop')
def stop_process():
    try:
        wait, driver = start_browser()
        pid = request.args.get("pid")
        existing_process = Message.query.filter(
            Message.id == int(pid)
        ).first()
        existing_process.on = False
        driver.close()
        return make_response("Stopped")
    except BaseException as e:
        print(e)


