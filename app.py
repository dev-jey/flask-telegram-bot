from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from flask import Flask, render_template, request
app = Flask(__name__)


options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=/Users/jey/Library/Application Support/Google/Chrome/Sel")


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
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.maximize_window()
    driver.get(link)
    driver.implicitly_wait(20)
    while True: 
        time.sleep(int(duration))
        textarea = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]").send_keys(message)
        driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[3]/button").click()
    
def close_windows():
    driver.close()
    driver.quit()


if __name__ == "__main__":
    app.run(debug=True)