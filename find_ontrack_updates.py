from tools.password_manager import PasswordManager
from tools.ontrack_ctrl import OntrackCtrl
from tools.single_signon import SingleSignon
from tools.ms_teams import send_teams_msg
from tools.logger import Logger
from tools.utils import ensure_directory_exists, load_from_file, write_to_file, refresh_auth_token

import os
import sys
from dotenv import load_dotenv

load_dotenv()
AUTH_TOKEN_FILE = "auth_token.txt"
LOGGING_DIRECTORY = "./logs"

ensure_directory_exists(LOGGING_DIRECTORY)
logger = Logger(LOGGING_DIRECTORY)


def get_auth_token(run_headless=True, verbose=True):
    try:
        sso = SingleSignon('./chromedriver.exe', run_headless, verbose)
        token = sso.get_auth_token(os.getenv('USER'), PasswordManager.decrypt(os.getenv('KEY'), os.getenv('PASS')))
        write_to_file(token, AUTH_TOKEN_FILE)
        logger.success("retrieved token after MFA check")
        return token
    except Exception as e:
        logger.error(f"retrieving token using selenium - {e}")
        print(f"Error attempting to retrieve auth token - {e}")
        sys.exit()

def load_token():
    token = load_from_file(AUTH_TOKEN_FILE)
    # if the token isn't found in the file, it uses the SSO module to run the Ontrack login process (this will require the user to authorize using MFA)
    if not token:
        logger.log("unable to retrieve auth token from file")
        print("Couldn't get auth token from file - running selenium")
        token = get_auth_token()


    # detects if the token input from auth_token.txt is expired.
    # If it is, the SSO login process needs to be done again
    token = refresh_auth_token(os.getenv('USER'), token)

    if not token:
        logger.log("auth token from file is expired")
        print("Got invalid auth token from file - running selenium")
        token = get_auth_token()
    else:
        logger.success("refreshed authentication token")

    return token


if __name__ == "__main__":
    if not os.getenv('KEY'):
        logger.error("couldnt get values from env file")
        print("Run generate_env_file.py to create a .env file")
        sys.exit()

    if os.getenv('WEBHOOK') == '<Your-Webhook-Url-Here>':
        logger.error("no webhook url set")
        print("Edit WEBHOOK in the .env file - Put in your own webhook url")
        sys.exit()


    try:
        # attempt to retrieve a saved token from a local text file
        # if that fails, use Selenium to automate the process of Deakin single-signon
        # this will require a MFA check
        token = load_token()
        print("Accessing Ontrack API")
        o = OntrackCtrl(os.getenv('USER'), token, use_all_units = False)

        # set some random comments to be unread to ensure we receieve a ms teams message
        # setting comments to unread seems to be broken in ontrack atm...
        # o.set_random_tasks_unread(1)

        msg = o.get_updates_msg()

        if msg:
            send_teams_msg(os.getenv('WEBHOOK'), msg)
            logger.success("sent ms teams message")
            print("Sent a teams message")
        else:
            logger.log("no updates")
            print("no updates")

    except Exception as e:
        logger.error(f"accessing ontrack api {e}")
        print("Error accessing ontrack API")
        sys.exit()


