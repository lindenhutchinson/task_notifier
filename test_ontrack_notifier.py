
from tools.ontrack_ctrl import OntrackCtrl
from tools.single_signon import SingleSignon
from tools.ms_teams import send_teams_msg
import os
from tools.utils import ensure_directory_exists, write_to_file
from dotenv import load_dotenv
load_dotenv()
def test_ontrack_notifier(username, password, webhook_url, use_all_units):
    # this object will handle the automated browser that signs into deakin single sign-on
    sso = SingleSignon('./chromedriver.exe', headless=False)

    print("Getting auth token")
    token = sso.get_auth_token(username, password)

    print(f"Accessing ontrack")
    ontrack = OntrackCtrl(username, token, use_all_units)

    # set some random comments to be unread so something shows up in the notification
    # this feature seems to be broken in the current version of ontrack 7/07/22
    ontrack.set_random_tasks_unread(3) 

    # retrieve the data needed to craft the message
    msg = ontrack.get_updates_msg()
    if msg:
        send_teams_msg(webhook_url, msg)
        print("Sent a teams message")
    else:
        print("Found no updates")
        
if __name__ == "__main__":
    # REPLACE THESE VALUES #############################################
    username = os.getenv('USER') or 'YOUR ONTRACK USERNAME'
    webhook_url = os.getenv('WEBHOOK') or 'YOUR MSTEAMS WEBHOOK URL'

    # use all units if you don't have any current ontrack units
    # or if you haven't got any messages in the current units
    use_all_units = True  
    ####################################################################

    password = input("Enter your deakin password: ")
    os.system('cls')
    test_ontrack_notifier(username, password, webhook_url, use_all_units)
