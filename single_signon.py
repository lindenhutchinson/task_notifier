from selenium import webdriver
import time
import json
import sys
import urllib.parse


# use this constant to allow selenium more time to find elements
SLEEP_TIME = 10

# used to determine how many times selenium should retry finding an element on the browser
SEL_RETRIES = 3


class SingleSignon:
    def __init__(self, user, p, selenium_dir, run_headless, verbose):
        self.username = user
        self.password = p
        self.sel_dir = selenium_dir
        self.run_headless = run_headless
        self.verbose = verbose
        self.driver = self.make_web_driver()

    # create selenium driver to access ontrack webpage

    def make_web_driver(self):
        if self.verbose:
            print("Loading selenium...")
        chrome_options = webdriver.ChromeOptions()
        if self.run_headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--enable-javascript")
        chrome_options.add_argument("--no-sandbox");
        chrome_options.add_argument("--disable-dev-shm-usage");
        driver = webdriver.Chrome(
            options=chrome_options, executable_path=self.sel_dir)

        if self.verbose:
            print("Accessing ontrack page that will redirect us to authentication")
        driver.get("https://ontrack.deakin.edu.au/#/home")
        if self.verbose:
            print("Page loaded. We will sleep for {} seconds now".format(SLEEP_TIME))
        time.sleep(SLEEP_TIME)
        return driver

    def try_get_ele_by_id(self, id):
        count = 0
        while(count != SEL_RETRIES):
            try:
                return self.driver.find_element_by_id(id)
            except:
                count += 1
                if self.verbose:
                    print("Attempt {}. Couldn't find {}. Will retry in {} seconds".format(count, id, SLEEP_TIME))
                time.sleep(SLEEP_TIME)


        if self.verbose:
            print("Couldn't find {} after max retries. Quitting...".format(id)) 
        sys.exit(0)


    def try_get_ele_by_class_name(self, name):
        count = 0
        while(count != SEL_RETRIES):
            try:
                return self.driver.find_element_by_class_name(name)
            except:
                count+=1
                if self.verbose:
                    print("Attempt {}. Couldn't find {}. Will retry in {} seconds".format(count,name,SLEEP_TIME)) 
                time.sleep(SLEEP_TIME)


        if self.verbose:
            print("Couldn't find {} after max retries. Quitting...".format(name)) 
        sys.exit(0)

    def is_text_present(self, text):
        return str(text) in self.driver.page_source

    # login to the ontrack site via selenium
    def login_ontrack(self):
        if self.verbose:
            print("Logging in to ontrack...") 
        
        name_input = self.try_get_ele_by_id("username")
        name_input.send_keys(self.username)
        pass_input = self.try_get_ele_by_id("password") 
        pass_input.send_keys(self.password.decode())
        signin_button = self.try_get_ele_by_class_name("btn--login")
        signin_button.click()
        if self.verbose:
            print("Have clicked the first sign in button. Will now sleep for {} seconds".format(SLEEP_TIME)) 

        time.sleep(SLEEP_TIME)

        if self.is_text_present('The service you are trying to access is connected to the Australian Access Federation. Select your organisation below to log in.'):
            if self.verbose:
                print("We have logged in")
        else:
            if self.verbose:
                print("Something has gone wrong with the deakin authentication")
            raise ValueError('Unable to login to Deakin Single Signon.')



        signin_button = self.try_get_ele_by_class_name("btn--login")
        signin_button.click()
        if self.verbose:
            print("Just clicked the second sign in button. Will now sleep for {} seconds".format(SLEEP_TIME))
        time.sleep(SLEEP_TIME)

        self.logged_in = True
        if self.verbose:
            print("Ideally we should be authenticated with DSS now. Will now access the ontrack homepage again")
        self.driver.get("https://ontrack.deakin.edu.au/#/home")
        if self.verbose:
            print("Selenium has loaded the ontrack page, but we will give it {} seconds to fully load".format(SLEEP_TIME*2))
        time.sleep(SLEEP_TIME*2)

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
            if self.verbose:
                print("ERROR: Couldn't find auth token in cookies")

            raise ValueError("Couldn't find the ontrack auth token in the browser cookies")


        deakin_id = json.loads(urllib.parse.unquote(auth))
        auth_token = deakin_id['authenticationToken']
        if self.verbose:
            print("We're in business, we've got the auth token. The next part will be much faster")

        self.driver.quit()

        return auth_token

