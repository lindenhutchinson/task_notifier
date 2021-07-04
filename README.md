# Task Notifier

A python program for alerting you when you have received responses on Ontrack.

![Image of Microsoft Teams messages](screenshots/webhook_msg.png?raw=true)

## How to Run

0. Ensure that your DUO Multi-Factor Authentication settings have been set to always send a notification. This is very important as the automated web browser is unable to click the button to send you a notification. If you aren't receiving MFA checks when you think you should be, double check your DUO settings

1. Download the [chromedriver version](https://chromedriver.chromium.org/downloads) appropriate to your chrome version

2. Create a virtual env to run the program in

   ```python
   pip install virtualenv
   virtualenv venv
   source venv/Scripts/activate
   ```

3. Install requirements.txt

   ```python
   pip install -r requirements.txt
   ```

4. Create a Microsoft Teams group and create a channel webhook by following [this tutorial](https://techcommunity.microsoft.com/t5/microsoft-365-pnp-blog/how-to-configure-and-use-incoming-webhooks-in-microsoft-teams/ba-p/2051118)

5. Change the username and webhook_url values in **test_ontrack_notifier.py** The password is currently set to use input to avoid having to store a password in plaintext.

6. Run **test_ontrack_notifier.py**. This will require you to authorize the login via MFA. It will randomly set some comments to be unread to ensure there's some notifications to be sent

>If you don't have any ontrack units in the current teaching period but would still like to test out the program, you should set **use_all_units** to true.

## Generating an .env file

1. If you would like to setup a more permanent runner of the script, you can generate an env file to store your credentials in by using **generate_env_file.py**
**Please keep in mind this is NOT a secure way to store your credentials. The key to your encrypted password is stored in the same file. It only stops someone looking over your shoulder from easily seeing your password**

## Crontab

>requires .env file

If you'd like to setup a scheduling runner for this script such as Crontab, you should use **find_ontrack_updates.py**

You will need to put your webhook url into the correct location in the .env file

`WEBHOOK=<Your-Webhook-Url-Here>`

Now you run **find_ontrack_updates.py**

This is similar to **test_ontrack_notifier.py** but has error handling and logging. It will still require you to authorize via MFA the first time you run it. After the first run, your auth token is saved to a file and subsequent runs attempt to use that token rather than having to re-authorize with MFA.

## Download All Task PDF files

>requires .env file

1. You can use **write_tasks_to_pdf** to download all the ungraded tasks from your active units into a directory format similar to the one outlined below

   ```md
   📦units
    ┃
    ┣ 📂SIT314
    ┃ ┣ 📜1.1P.pdf
    ┃ ┣ ...
    ┃ ┗ 📜9.1P.pdf
    ┃
    ┗ 📂SIT315
    ┃ ┣ 📜M1.T1P.pdf
    ┃ ┣ ...
    ┃ ┗ 📜Task M3.T3D.pdf
   ```
