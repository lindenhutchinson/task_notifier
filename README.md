# Task Notifier

A python program for alerting you when you have received responses on Ontrack.

![Image of Microsoft Teams messages](screenshots/webhook_msg.png?raw=true)

## How to Run

0. Ensure that your DUO Multi-Factor Authentication settings have been set to always send a notification. This is very important as the automated web browser is unable to click the button to send you a notification. If you aren't receiving MFA checks when you think you should be, double check your DUO settings

1. Download the [chromedriver version](https://chromedriver.chromium.org/downloads) appropriate to your chrome version

2. Create a virtual env to run the program in

```
pip install virtualenv
virtualenv venv
source venv/Scripts/activate
```

3. Install requirements.txt

```
pip install -r requirements.txt
```

4. Create a Microsoft Teams group and create a channel webhook by following [this tutorial](https://techcommunity.microsoft.com/t5/microsoft-365-pnp-blog/how-to-configure-and-use-incoming-webhooks-in-microsoft-teams/ba-p/2051118)

5. Change the username and webhook_url values in **main.py** The password is currently set to use input to avoid having to store a password in plaintext (change this if you don't care).

```
username = 'your-deakin-username'
webhook_url = 'your-webhook-url'
password = input("Enter your deakin password: ")
use_all_units = False
```

6. Running main.py will require you to authorize the login via MFA. It will randomly set some comments to be unread to ensure there's some notifications to be sent
>If you don't have any ontrack units in the current teaching period but would still like to test out the program, you should set **use_all_units** to true.
```
sso = SingleSignon('./chromedriver.exe')

token = sso.get_auth_token(username, password) # requires MFA

ontrack = OntrackCtrl(username, token, use_all_units)

ontrack.set_random_tasks_unread(3) 

msg = ontrack.get_updates_msg()

send_teams_msg(webhook_url, msg)
```


## Crontab

1. If you would like to setup a more permanent runner of the script, you can generate an env file to store your credentials in by using **generate_env_file.py**

2. You will need to put your webhook url into the correct location in the .env file

```
WEBHOOK=<Your-Webhook-Url-Here>
```

3. Now you can run **find_ontrack_updates.py**. This is similar to main.py but has error handling and logging (ideal for running on crontab). It will still require you to authorize via MFA the first time you run it. After the first run, your auth token is saved to a file and subsequent runs attempt to use that token rather than having to re-authorize with MFA.
