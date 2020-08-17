# task_emailer

A little script I wrote for convenience. I wanted to get emails when I got updates on my tasks on ontrack.

It uses selenium to log in to Deakin Single Signon, and retrieves an ontrack authentication token from the cookies in the automated browser.
After that's done, which takes the majority of the running time, it uses the auth token to access the ontrack api

If that kinda automation isn't your thing, you can always go into your own browser, copy the ontrack authentication token from there and then create the Ontrack object by passing the auth token you have copied. 

At this point, it's as easy as accessing some urls and filtering the JSON data to find the tasks that have updates

The script uses SMTP to send emails to a designated address.
If you want to use a gmail account as the sender, you will need to have its access level set to lowest security

The function get_updated_email() will call the required functions to check every unit for any task updates, then formats and sends these as an email

The script is set up to run on a crontab

single_signon.py contains two constants, SLEEP_TIME and SEL_RETRIES
If the script is failing in the selenium stage, these may need to be tinkered with.
