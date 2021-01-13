import os
from selenium import webdriver
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session, jsonify, abort
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from flask_login import login_required, current_user
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from .models import Message

'''Helper Functions'''

class TelegramFunctionality(object):
    ''' Different helper functions for accessing Telegram'''
    def __init__(self, driver=None, driver2=None, process=None):
        self.driver = driver
        self.driver2 = driver2
        self.process = process


    def check_chrome_driver_path(self, options):
        try:
            if os.environ.get('FLASK_ENV') == 'production':
                self.driver = webdriver.Chrome(executable_path=str(
                    os.environ.get('CHROMEDRIVER_PATH')), options=options)
            else:
                self.driver = webdriver.Chrome(
                    ChromeDriverManager().install(), options=options)
            return self.driver
        except Exception as e:
            print(e)
            return make_response(f"We are having trouble processing your request. Please check your internet connection", 400)


    def try_to_login(self, wait, code, mobile_no, logger):
        self.driver.get('https://web.telegram.org/#/login')
        wait.until(
            lambda driver: driver.current_url == 'https://web.telegram.org/#/login')
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input")))
        # Codefield
        code_field = self.driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[1]/input"
        )
        code_field.clear()
        code_field.send_keys(code)
        # MobileField
        mobile_field = self.driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
        )
        mobile_field.clear()
        mobile_field.send_keys(mobile_no)
        self.driver.implicitly_wait(3)
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div[2]/input"
        ).send_keys(Keys.ENTER)

        try:
            wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//button[@ng-click='$close(data)']"))
            )
            self.driver.find_element_by_xpath(
                "//button[@ng-click='$close(data)']").click()
        except BaseException as e:
            # close_driver(driver)
            logger.error(f'An error occurred: {e}')
            return make_response(f"We are experiencing a problem sending the code", 400)



    def check_if_multiple_sends(self, logger):
        try:
            # Check for too many times error
            too_many_times = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//button[@ng-click='$dismiss()']")))
            if too_many_times:
                TelegramFunctionality.close_driver(self)
                return True
        except BaseException as e:
            logger.info("2. Success, No too many times error")
            return False

    @staticmethod
    def close_driver(self):
        self.driver.close()
        self.driver.quit()

    def check_code_sent(self):
        try:
            self.driver.find_element_by_xpath("//input[@ng-model='credentials.phone_code']").is_displayed()
            return True
        except:               
            self.driver.close()
            self.driver.quit()
            return False


    def validate_verification_code(self, my_code):
        if my_code == "" or my_code is None:
            return make_response(f"Enter a verification code", 400)
        if len(my_code) != 5:
            return make_response(f"Code must be  5 digits.", 400)


    def get_current_process_from_db(self, pid):
        try:
            self.process = Message.query.filter(
                Message.id == int(pid)
            ).first()
        except:
            return make_response(f"We are having trouble processing your request.", 400)
        return self.process

    def connect_to_existing_driver(self):
        try:
            self.driver2 = webdriver.Remote(
                command_executor=self.process.executor_url, desired_capabilities={})
            return self.driver2
        except Exception as e:
            print(e)
            return make_response(f"We are having trouble processing your request. Please check your internet connection", 400)

    def search_channel(self, logger):
        try:
            search_results = self.driver2.find_elements_by_xpath(
                "//a[@ng-mousedown='dialogSelect(myResult.peerString)']")
            search_results_alternate = self.driver2.find_elements_by_xpath(
                "//a[@ng-mousedown='dialogSelect(dialogMessage.peerString, dialogMessage.unreadCount == -1 && dialogMessage.mid)']"
            )
            if len(search_results) == 0 and len(search_results_alternate) == 0:
                TelegramFunctionality.close_driver(self)
                return make_response("The channel or group name was not found", 404)
        except BaseException as e:
            logger.info('Search results found')
        return {"search_results":search_results, "search_results_alternate": search_results_alternate}


    def check_channel_details(self, search_results, search_results_alternate, logger):
        if search_results:
            self.driver2.find_elements_by_xpath(
                "//a[@ng-mousedown='dialogSelect(myResult.peerString)']")[0].click()
        if search_results_alternate:
            self.driver2.find_elements_by_xpath(
                "//a[@ng-mousedown='dialogSelect(dialogMessage.peerString, dialogMessage.unreadCount == -1 && dialogMessage.mid)']")[0].click()
        channel_name = self.driver2.find_element_by_xpath(
            "//span[@my-peer-link='historyPeer.id']").text
        channel_members = None
        can_send = None
        try:
            channel_members = self.driver2.find_element_by_xpath(
                "//span[@my-chat-status='-historyPeer.id']").text
            can_send = self.driver2.find_element_by_xpath(
                    "/html/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]").is_displayed()
        except:
            pass
        logger.info(f"Channel Name: {channel_name}")
        logger.info(f"Channel_members: {channel_members}")
        return {"channel_name": channel_name, "channel_members": channel_members, "can_send": can_send}