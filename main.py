from password_manager import PasswordManager
from ontrack import Ontrack
from single_signon import SingleSignon
from emailer import Emailer
import os

def get_key_from_file(dir):
    with open(dir, 'r') as fn:
        return fn.read().encode('utf-8')

# use this function to generate a key to save in a local file
# and an encrypted password, to be used on the document or as an environment variable
# these need to be input as bytes using encode("utf-8")
def print_key_and_pass(password):
    p = PasswordManager(password)
    key = p.make_key()
    e_pass = p.encrypt(password)

    print("Key: {}".format(key))
    print("Encrypted Password: {}".format(e_pass))

if __name__ == "__main__":
    # use this function to print out a new encryption key and an encrypted password
    # You will need to encode("utf-8") your password

    # print_key_and_pass('testing'.encode("utf-8"))



    current_file_dir = os.path.dirname(__file__)
    # local files that contain encryption keys for the passwords
    ekey = get_key_from_file(os.path.join(current_file_dir, "ekey"))
    dkey = get_key_from_file(os.path.join(current_file_dir, "dkey"))

    # encrypted passwords stored as env variables
    ep = os.environ['EMAIL_PASS'].encode('utf-8')
    dp = os.environ['DEAKIN_PASS'].encode('utf-8')

    # Or you could have those hardcoded in the document

    # ekey = b'this is where i could paste my encryption key for my email password'
    # I decided on using two keys, for some reason. You make your own decisions
    # dkey = b'this is where i could paste my encryption key for my deakin password'

    # dp = b'this-is-where-i-would-paste-my-encrypted-deakin-password'
    # ep = b'this-is-where-i-would-paste-my-encrypted-email-password'


    e_pm = PasswordManager(ep)
    e_pm.use_key(ekey)

    d_pm = PasswordManager(dp)
    d_pm.use_key(dkey)


    sender_email = ''
    receiver_email = ''
    deakin_username = ''

    emailer = Emailer(sender_email, e_pm, receiver_email)

    # driver_path = os.path.join(current_file_dir, "chromedriver")
    # run_selenium_headless = False
    # ss = SingleSignon(deakin_username, d_pm, driver_path, run_selenium_headless)

    # for simply playing around with the script, it's often easier to get the auth token from your browser
    # then pass it into the Ontrack constructor
    # auth_token = ss.get_auth_token()
    o = Ontrack('auth_token_here', emailer)

    proj_id = 18033
    task_def_id = 3700
    task_def_id = ''
    weeks_requested = 1
    print(o.request_extension(proj_id, task_def_id,task_def_id, weeks_requested))




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

