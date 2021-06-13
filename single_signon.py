from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import urllib
import json
from dotenv import load_dotenv
from password_manager import PasswordManager
import os


class SingleSignon:
    def __init__(self, selenium_dir, verbose=False, run_headless=True):
        self.run_headless = run_headless
        self.verbose = verbose
        self.driver = self.make_web_driver(selenium_dir)

    # create selenium driver to access ontrack webpage
    def make_web_driver(self, selenium_dir):
        chrome_options = webdriver.ChromeOptions()
        if self.run_headless:
            chrome_options.add_argument('--headless')
            
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--enable-javascript")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(
            options=chrome_options, executable_path=selenium_dir)

        return driver


    def wait_for_element_presence(self, identifier, wait_time=10, frequency=0.5):
        try:
            element = WebDriverWait(self.driver, wait_time, frequency).until(EC.presence_of_element_located(identifier))
        except TimeoutException:
            print("Timed out waiting for element. Please try again")
            sys.exit()
        
        return element

    def verbose_msg(self, msg):
        if self.verbose:
            print(msg)

    def get_auth_token(self, username, password):
        self.driver.get('https://ontrack.deakin.edu.au/#/home')
        self.verbose_msg("Loading SSO login page")

        self.login(username, password)
        self.verbose_msg("Submitted username and password - waiting for MFA")

        self.wait_for_mfa()
        self.verbose_msg("MFA has been accepted - getting auth token")

        auth_token = self.wait_for_cookie()
        self.verbose_msg("Retrieved auth token")

        return auth_token

    def login(self, username, password):
        u_input = self.wait_for_element_presence((By.ID, "username"))
        p_input = self.wait_for_element_presence((By.ID, "password"))
        submit_btn = self.wait_for_element_presence((By.CLASS_NAME, "btn--login"))

        u_input.send_keys(username)
        p_input.send_keys(password)
        submit_btn.click()

    def wait_for_mfa(self):
        continue_btn = self.wait_for_element_presence((By.NAME, "_eventId_proceed"), 60, 1)
        continue_btn.click()

    def wait_for_cookie(self):
        cookie=None
        ctr=0
        while(cookie == None):
            cookie = self.driver.get_cookie("doubtfire_user")
            time.sleep(0.5)
            ctr +=1
            if ctr == 60:
                print("Couldn't find cookie after 30 seconds. Please try again")
                sys.exit()

        cookie_fields = json.loads(urllib.parse.unquote(cookie['value']))
        auth_token = cookie_fields['authenticationToken']
        return auth_token
    

if __name__ == "__main__":
    sso = SingleSignon('./chromedriver.exe', run_headless=True, verbose=True)
    token = sso.get_auth_token(os.getenv('USER'), PasswordManager.decrypt(os.getenv('KEY'), os.getenv('PASS')))
    print(token)
