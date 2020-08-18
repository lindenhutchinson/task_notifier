# task_emailer

A little script I wrote so I could receive emails when my tasks have been updated on ontrack. It didn't natively have this feature, so I figured out how to access the api. 
Then I wrote a program to check for updates and email me if my tutors have marked any of my tasks off or replied to my messages.
I run this on crontab on my raspberry pi

## Password_Manager

There is a password encryption manager I wrote that uses symmetric encryption so there's no need to store passwords in plaintext.
To use this, you'll first need to run the below function to generate a key and your encrypted password string.

print_key_and_pass('your-password-here'.encode("utf-8"))

I do this twice for each password (email and deakin) but you could use the same key twice.

I save the key in a local file and the encrypted password is stored either in an environment variable or directly on the document.
The password_manager class only deals with values in bytes so when you're passing strings directly, use .encode("utf-8")

## Main

If you want to use selenium, you'll probably want to check some of these out:

* string driver_path
* bool run_selenium_headless
* bool verbose

They do pretty much what's on the box.

## Single Signon

It uses selenium to log in to Deakin Single Signon, and retrieves an ontrack authentication token from the cookies in the automated browser.
This process takes the longest amount of time, because selenium is so slow and prone to skipping over elements that it's looking for.

There are two constants at the top of single_signon.py

* SLEEP_TIME
* SEL_RETRIES

There are a number of sleeps in the program to give selenium plenty of time to find what it's looking for.
Depending on your system, you may need to increase the sleep time.

SEL_RETRIES is the number of times the program will attempt to search for an element on the webpage. 
This will sleep between every attempt and will exit the program if it doesn't find the element after the set amount of times.

Upon finding the authentication token in the cookies after your automated login to ontrack, the actual accessing the API is a lot faster.

If you don't want to mess around with selenium and just want to try out the script, you can easily pass in an auth_token from your browser, created after you login.
You can find this by pressing F12 then going to the network tab. From here it should be easy to see some urls that look like

	https://ontrack.deakin.edu.au/api/projects?auth_token=AUTH TOKEN WILL BE HERE&include_inactive=true

just paste that value into the Ontrack constructor and you'll skip the entire slow part of the script.
Ontrack(auth_token, emailer)

## Emailer

The script uses SMTP to send emails to a designated address.
If you want to use a gmail account as the sender, you will need to have its access level set to lowest security

The function get_updated_email() will call the required functions to check every unit for any task updates, then formats and sends these as an email



