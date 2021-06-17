
from tools.ontrack_ctrl import OntrackCtrl
from tools.single_signon import SingleSignon
from tools.ms_teams import send_teams_msg
import os

def test_ontrack_notifier(username, password, webhook_url, use_all_units):
    sso = SingleSignon('./chromedriver.exe')
    token = sso.get_auth_token(username, password)
    print(f"Accessing ontrack")
    ontrack = OntrackCtrl(username, token, use_all_units)
    ontrack.set_random_tasks_unread(3) # set some random comments to an unread state
    msg = ontrack.get_updates_msg()
    send_teams_msg(webhook_url, msg)
    print("Sent a teams message")


if __name__ == "__main__":
    username = 'Your ontrack username'
    webhook_url = 'Your webhook url'

    password = input("Enter your deakin password: ")
    os.system('cls')

    # change this to True if you don't have any active ontrack units
    use_all_units = False  
    
    test_ontrack_notifier(username, password, webhook_url, use_all_units)
