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
    except Exception:
        print("Error attempting to retrieve auth token")
        print(e)
        sys.exit()

if __name__ == "__main__":
    token = load_auth_token()
    if not token:
        print("Couldn't get auth token from file - running selenium")
        token = get_token()
       
    o = Ontrack(os.getenv('USER'), token)
    token = o.refresh_auth_token()
    if not token:
        print("Got invalid auth token from file - running selenium")
        token = get_token()

    try:
        print("Accessing Ontrack API")
        o.mark_comment_unread(28230, 4364, 1262750)
        o.mark_comment_unread(28230, 4367, 1275962)
        o.mark_comment_unread(28230, 4772, 1634244)
        # o.mark_comment_unread(18033, 3424, 797843)
        # o.mark_comment_unread(18033, 3424, 797844)
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
