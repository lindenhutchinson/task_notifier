
from tools.ontrack_ctrl import OntrackCtrl
from tools.single_signon import SingleSignon
from tools.ms_teams import send_teams_msg
import os
from tools.utils import ensure_directory_exists, write_to_file

def test_ontrack_notifier(username, password, webhook_url, use_all_units):
    sso = SingleSignon('./chromedriver.exe')
    token = sso.get_auth_token(username, password)
    print(f"Accessing ontrack")
    ontrack = OntrackCtrl(username, token, use_all_units)
    ontrack.set_random_tasks_unread(3) # set some random comments to an unread state
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

    # change this to True if you don't have any active ontrack units
    use_all_units = False  
    ####################################################################

    password = input("Enter your deakin password: ")
    os.system('cls')
    test_ontrack_notifier(username, password, webhook_url, use_all_units)
