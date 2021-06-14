
from ontrack import Ontrack
from single_signon import SingleSignon
from ms_teams import send_teams_msg

def test_ontrack_notifier(username, password, webhook_url, use_all_units):
    sso = SingleSignon('./chromedriver.exe', run_headless=True, verbose=True)
    token = sso.get_auth_token(username, password)
    print(f"Accessing ontrack")
    ontrack = Ontrack(username, token, use_all_units)
    ontrack.set_random_tasks_unread(3) # set some random comments to an unread state
    msg = ontrack.get_update_msg()
    send_teams_msg(webhook_url, msg)


if __name__ == "__main__":
    username = 'your-deakin-username'
    password = 'your-deakin-password'
    webhook_url = 'your-webhook-url'
    use_all_units = False 
    # change this to true if you currently don't have any active ontrack units
    # keep in mind that including all units can slow down the script considerably

    test_ontrack_notifier(username, password, webhook_url, use_all_units)
