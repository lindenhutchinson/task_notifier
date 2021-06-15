# Task Notifier

A python program for alerting you when you have received responses on Ontrack.

To run this program:

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

5. Change the required values in main.py and run it. The password variable is currently set to use input to avoid having to store a password in plaintext (change this if you don't care).
Running main.py will require you to authorize the login via MFA and will randomly set some comments from units in the current teaching period to unread.
If you currently don't have any ontrack units in the current teaching period but would still like to test out the program, you can set the use_all_units variable to True. This may slow the script execution down depending on how many ontrack units you have completed.

```
    username = 'your-deakin-username'
    password = input("Enter your deakin password: ")
    webhook_url = 'your-webhook-url'
    use_all_units = False
```

6. If you would like to setup a more permanent runner of the script, you can generate a .env file by running generate_env_file.py

```
    python generate_env_file.py
```

7. Put your webhook url into the correct location in the .env file

```
    WEBHOOK=<Your-Webhook-Url-Here>
```

8. After setting up the .env file, you can run find_ontrack_updates. You could be set this up to run on a crontab every 45 minutes or so and it will keep the authentication token refreshed so that you will (ideally) only need to do the one MFA check.

## single_singon.py

This module uses Selenium webdriver to automate the process of SSO login.

SSO uses variables contained in a .env file which are generated using generate_env_file.py

This function takes in username and password input.

Your password is encrypted using symmetric encryption and the key, username and encrypted password are stored in the .env file

Storing a key and password together isn't really that different to storing the password in plaintext for someone who knows even a little. Keep that .env file safe or find a different way to store your password.

**Running this module will require you to manually authorize the login via MFA**

**You need to ensure your MFA is set to always send a notification.**

This is important as the script is unable to click the button to send you a notification; it depends on you having checked DUO setting of always sending a notification to your device

After the SSO process have been completed, the auth token generated will be saved to a text file (auth_token.txt)

In subsequent runs of the program, the content from this file will be used rather than having to run the SSO login process again and avoiding unnecessary MFA checks

Each time the program is run, the token will be refreshed giving you another 60 minutes of token validity.

If you set it up to run on crontab every 59 minutes, you would only have to do the one MFA and hypothetically, it could use the same auth token forever (until you inevitably have to login to ontrack yourself and forcibly generate a new auth token)

## ontrack_ctrl.py

This module operates the accessing of the ontrack API endpoints.

Using the auth token generated from single_signon.py to authorize the requests, it's possible to comb through the messages of all the tasks from all of your units in the current teaching period, and build up a list of new messages.
