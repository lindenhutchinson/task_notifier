from password_manager import PasswordManager
from ontrack import Ontrack
from single_signon import SingleSignon
from emailer import Emailer
from ms_teams import send_teams_msg
import os
from datetime import datetime
import sys
from dotenv import load_dotenv


def save_auth_token(token):
    with open("auth_token.txt", "w") as fn:
        fn.write(token)


def load_auth_token():
    try:
        with open("auth_token.txt", "r") as fn:
            return fn.read()
    except FileNotFoundError:
        return None

def get_token(run_headless=True, verbose=True):
    try:
        sso = SingleSignon('./chromedriver.exe', run_headless, verbose)
        token = sso.get_auth_token(os.getenv('USER'), PasswordManager.decrypt(
            os.getenv('KEY'), os.getenv('PASS')))
        save_auth_token(token)
        return token
    except Exception as e:
        print("Error attempting to retrieve auth token")
        print(e)
        sys.exit()

if __name__ == "__main__":
    # attempts to load the auth token from auth_token.txt
    token = load_auth_token()
    # if the token isn't found in the file, it uses the SSO module to run the Ontrack login process (this will require the user to authorize using MFA)
    if not token:
        print("Couldn't get auth token from file - running selenium")
        token = get_token()
       
    o = Ontrack(os.getenv('USER'), token)
    # refresh the token, so if this script is run every 60 minutes, it shouldn't have to repeat the MFA process as the token will stay valid
    token = o.refresh_auth_token()
    # this also detects if the token input from auth_token.txt is expired. If it is, the SSO login process needs to be done again
    if not token:
        print("Got invalid auth token from file - running selenium")
        token = get_token()

    o = Ontrack(os.getenv('USER'), token)

    try:
        print("Accessing Ontrack API")

        # this will randomly set tasks to an unread state (how nice of the doubtfire developers to include that endpoint)
        # the program will find the "new" messages and send a ms teams notification
        o.set_random_tasks_unread(5)

        # find all new comments from the current teaching period's units
        msg = o.get_update_msg()

    except Exception as e:
        print("Error accessing ontrack API")
        print(e)
        sys.exit()

    try:
        send_teams_msg(os.getenv('WEBHOOK'), msg)
        print("Sent a teams message")
    except Exception as e:
        print("Error accessing MS Teams webhook")
        print(e)
        sys.exit()
