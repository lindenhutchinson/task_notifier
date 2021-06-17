from tools.password_manager import PasswordManager
from tools.ontrack_ctrl import OntrackCtrl
from tools.single_signon import SingleSignon
from tools.ms_teams import send_teams_msg
from tools.logger import Logger
from tools.utils import ensure_directory_exists, load_from_file, write_to_file

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
        print("Error attempting to retrieve auth token")
        sys.exit()


if __name__ == "__main__":
    if not os.getenv('KEY'):
        logger.error("couldnt get values from env file")
        print("Run generate_env_file.py to create a .env file")
        sys.exit()

    if os.getenv('WEBHOOK') == '<Your-Webhook-Url-Here>':
        logger.error("no webhook url set")
        print("Edit WEBHOOK in the .env file - Put in your own webhook url")
        sys.exit()

    token = load_from_file(AUTH_TOKEN_FILE)
    # if the token isn't found in the file, it uses the SSO module to run the Ontrack login process (this will require the user to authorize using MFA)
    if not token:
        logger.log("unable to retrieve auth token from file")
        print("Couldn't get auth token from file - running selenium")
        token = get_auth_token()

    o = OntrackCtrl(os.getenv('USER'), token)
    # refresh the token, so if this script is run every 60 minutes, it shouldn't have to repeat the MFA process as the token will stay valid
    token = o.refresh_auth_token()
    # this also detects if the token input from auth_token.txt is expired. If it is, the SSO login process needs to be done again
    if not token:
        logger.log("auth token from file is expired")
        print("Got invalid auth token from file - running selenium")
        token = get_auth_token()
    else:
        logger.success("refreshed authentication token")

    o = OntrackCtrl(os.getenv('USER'), token)

    try:
        print("Accessing Ontrack API")
        # set some random comments to be unread to ensure we receieve a ms teams message
        o.set_random_tasks_unread(3)
        msg = o.get_updates_msg()
    except Exception as e:
        logger.error(f"accessing ontrack {e}")
        print(f"Error accessing ontrack API {e}")
        sys.exit()



    try:
        send_teams_msg(os.getenv('WEBHOOK'), msg)
        logger.success("sent ms teams message")
        print("Sent a teams message")
    except Exception as e:
        logger.error(f"sending ms teams message {e}")
        print("Error accessing MS Teams webhook")
        sys.exit()


