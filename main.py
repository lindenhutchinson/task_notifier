from password_manager import PasswordManager
from ontrack import Ontrack
from single_signon import SingleSignon
from emailer import Emailer
import os
from datetime import datetime


current_file_dir = os.path.dirname(__file__)

def get_key_from_file(dir):
    with open(dir, 'r') as fn:
        return fn.read().encode('utf-8')

def write_to_file(file, text):
    with open(file, 'a+') as fn:
        fn.write(f"{text}\n")

# use this function to generate a key to save in a local file
# and an encrypted password, to be used on the document or as an environment variable
# these need to be input as bytes using encode("utf-8")
def print_key_and_pass(password):
    p = PasswordManager(password)
    key = p.make_key()
    e_pass = p.encrypt(password)

    print("Key: {}".format(key))
    print("Encrypted Password: {}".format(e_pass))

def get_time():
        return datetime.now().strftime("%H:%M")

if __name__ == "__main__":
    # use this function to print out a new encryption key and an encrypted password
    # You will need to encode("utf-8") your password or pass it as bytes - b'password'

    # print_key_and_pass('testing'.encode("utf-8"))
    
    dp = os.environ['DEAKIN_PASS'].encode('utf-8') # my encrypted deakin password stored as an env variable
    d_pm = PasswordManager(dp) # custom passwordmanager used so password is never stored in plaintext and only decrypted when it is used
    dkey = get_key_from_file(os.path.join(current_file_dir, "dkey"))  # local file containing the encryption key for my deakin password
    d_pm.use_key(dkey) # assigning the encryption key to the password manager
    deakin_username = os.environ['D_ACC'] # my deakin username stored as an env variable


    # used to log each time the program runs
    day = datetime.now().strftime("%Y-%m-%d")
    log_dir = os.path.join(current_file_dir, f"logs/{day}.txt")
  

    driver_path = '/usr/lib/chromium-browser/chromedriver'
    run_selenium_headless = True
    verbose = False


    # setting up the password manager for the emailer
    ekey = get_key_from_file(os.path.join(current_file_dir, "ekey"))
    ep = os.environ['EMAIL_PASS'].encode('utf-8')
    e_pm = PasswordManager(ep)
    e_pm.use_key(ekey)
    # creating the emailer
    sender_email = os.environ['S_EMAIL']
    receiver_email = os.environ['R_EMAIL']
    emailer = Emailer(sender_email, e_pm, receiver_email)


    try:
        ss = SingleSignon(deakin_username, d_pm, driver_path, run_selenium_headless, verbose)
        # for simply playing around with the script, it's easier to get the auth token from your browser
        # then paste it in here inplace of ss.get_auth_token()
        o = Ontrack(ss.get_auth_token())
        update_count=0
        results = o.get_updated_email()

        if results:
            email, update_count = results
            emailer.send_ontrack_msg(email, update_count)

            write_to_file(log_dir, f"{get_time()} - sent an email with {update_count} updates")
        else:
            write_to_file(log_dir, f"{get_time()} - program ran to completion but no updates were found")

    except Exception as e:
        if verbose:
            print(e)
        # used so I can quickly respond if the script stops working
        emailer.send_email("Uh oh, something went wrong with the last update check!\n{}".format(e)) 
        write_to_file(log_dir, f"{get_time()} - failed to send an email with this exception: {e}")



# some of the available functions. get_projects() is useful for testing the api is working.

# get_project_tasks(proj_id)
# returns a list of all tasks that have been released for a unit

# get_task_definitions(unit_id)
# returns json containing detailed information about a unit's tasks

# get_updated_tasks(proj)
# returns a dictionary of {task_name : comments} only for tasks that have num_new_comments > 0

# get_new_task_comments(proj_id, task_def_id)
# returns a list of comments that have is_new set to true in their json

# get_projects()
# return a list of all units that are in the current teaching period

# get_current_teaching_period()
# the name speaks for itself

# get_updated_email()
# send an email if there are any updated tasks

