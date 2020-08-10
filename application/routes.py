from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from flask import Flask, render_template, request
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import current_app as app


options = webdriver.ChromeOptions()


@app.route('/')
def home():
    return render_template("index.html")

@app.route("/get")
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
