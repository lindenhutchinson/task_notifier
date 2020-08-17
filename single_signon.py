from selenium import webdriver
import time
import json
import sys
import urllib.parse


# use this constant to allow selenium more time to find elements
SLEEP_TIME = 4

# used to determine how many times selenium should retry finding an element on the browser
SEL_RETRIES = 3

class SingleSignon:
    def __init__(self, user, p, selenium_dir, run_headless):
        self.username = user
        self.password = p
        self.sel_dir = selenium_dir
        self.run_headless = run_headless
        self.driver = self.make_web_driver()


    # create selenium driver to access ontrack webpage
    def make_web_driver(self):
        print("Loading selenium...")
        chrome_options = webdriver.ChromeOptions()
        if self.run_headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--enable-javascript")
        driver = webdriver.Chrome(
            options=chrome_options, executable_path=self.sel_dir)

        print("Attempting to load page")
        driver.get("https://ontrack.deakin.edu.au/#/home")
        print("Loaded! Waiting a little longer for good measure")
        time.sleep(SLEEP_TIME)
        return driver

    def try_get_ele_by_id(self, id):
        count = 0
        while(count != SEL_RETRIES):
            try:
                return self.driver.find_element_by_id(id)
            except:
                count+=1
                print("Attempt {}. Couldn't find {}. Will retry in {} seconds".format(count,id,SLEEP_TIME))
                time.sleep(SLEEP_TIME)


        print("Couldn't find {} after max retries. Quitting...".format(id))
        sys.exit(0)


    def try_get_ele_by_class_name(self, name):
        count = 0
        while(count != SEL_RETRIES):
            try:
                return self.driver.find_element_by_class_name(name)
            except:
                count+=1
                print("Attempt {}. Couldn't find {}. Will retry in {} seconds".format(count,name,SLEEP_TIME))
                time.sleep(SLEEP_TIME)


        print("Couldn't find {} after max retries. Quitting...".format(name))
        sys.exit(0)

        print("oops!!!")
    # login to the ontrack site via selenium
    def login_ontrack(self):
        print("Logging in to ontrack...")
        try:
            name_input = self.try_get_ele_by_id("username")
        except:
            print("Unable to find element the first time, trying it again!")
            time.sleep(SLEEP_TIME)
            name_input = self.try_get_ele_by_id("username")

        name_input.send_keys(self.username)
        pass_input = self.try_get_ele_by_id("password")
        pass_input.send_keys(self.password.decode())
        signin_button = self.try_get_ele_by_class_name("btn--login")
        signin_button.click()
        print("Logged in")
        time.sleep(SLEEP_TIME)
        signin_button = self.try_get_ele_by_class_name("btn--login")
        signin_button.click()
        print("Clicking through")
        time.sleep(SLEEP_TIME)
        self.logged_in = True

        print("hopefully we have some authentication now, let's try access ontrack...")
        self.driver.get("https://ontrack.deakin.edu.au/#/home")
        print("loaded ontrack page, we will give it plenty of time to load")
        time.sleep(SLEEP_TIME)

    # after logging in to ontrack, capture the created auth token so we can access the API
    def get_auth_token(self):
        self.login_ontrack()

        cookies = self.driver.get_cookies()

        auth = ''
        for cookie in cookies:
            if cookie['domain'] == 'ontrack.deakin.edu.au':
                auth = cookie['value']
                break

        if not auth:
            print("ERROR: Couldn't find auth token in cookies")
            sys.exit(0)

        identity = json.loads(urllib.parse.unquote(auth))
        auth_token = identity['authenticationToken']
        print("We're in business, we've got the auth token")
        self.driver.quit()

        return auth_token

