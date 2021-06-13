# Task Notifier 

A python program for alerting you when you have received responses on Ontrack.


To run this program:

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
4. Generate a .env file by running generate_env_file.py
```
    python generate_env_file.py
```
5. Create a Microsoft Teams group and create a channel webhook by following [this tutorial](https://techcommunity.microsoft.com/t5/microsoft-365-pnp-blog/how-to-configure-and-use-incoming-webhooks-in-microsoft-teams/ba-p/2051118)

6. Put the webhook url generated from the previous step into the appropriate location in the .env file
```
    WEBHOOK=<Your-Webhook-Url-Here>
```

7. Run main.py to check for new Ontrack messages. If any are found, a message will be sent via the MsTeams webhook
```
    python main.py
```

If you just want to test out your Microsoft teams webhook, you can randomly set tasks to unread in main.py using
```
Ontrack.set_random_tasks_unread()
```
before using
```
Ontrack.get_update_msg()
```
to retrieve the newly unread messages


## single_singon.py

This module uses Selenium webdriver to automate the process of SSO login.

SSO uses variables contained in a .env file which are generated using generate_env_file.py

This function takes in username and password input.

Your password is encrypted using symmetric encryption and the key, username and encrypted password are stored in the .env file

Storing a key and password together isn't really that different to storing the password in plaintext for someone who knows even a little. Keep that .env file safe or find a different way to store your password.


**Running this module will require you to manually authorize the login via MFA**

### You need to ensure your MFA is set to always send a notification. 
This is important as the script is unable to click the button to send you a notification; it depends on you having checked DUO setting of always sending a notification to your device

After the SSO process have been completed, the auth token generated will be saved to a text file (auth_token.txt)

In subsequent runs of the program, the content from this file will be used rather than having to run the SSO login process again and avoiding unnecessary MFA checks

Each time the program is run, the token will be refreshed giving you another 60 minutes of token validity.

If you set it up to run on crontab every 59 minutes, you would only have to do the one MFA and hypothetically, it could use the same auth token forever (until you inevitably have to login to ontrack yourself and forcibly generate a new auth token)


## ontrack.py

This module operates the accessing of the ontrack API endpoints.

Using the auth token generated from single_signon.py to authorize the requests, it's possible to comb through the messages of all the tasks from all of your units in the current teaching period, and build up a list of new messages.

A function quite useful for testing this feature is 
```
Ontrack.set_random_tasks_unread(5)
```
