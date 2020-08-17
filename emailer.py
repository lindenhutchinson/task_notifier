import smtplib


class Emailer:
    def __init__(self, sender, m, receiver):
        self.sender = sender
        self.sender_p = m
        self.receiver = receiver
        self.smtp_host = 'smtp.gmail.com'
        self.smtp_port = 587

    def send_email(self, message):
        s = smtplib.SMTP(self.smtp_host, self.smtp_port)
        s.starttls()
        s.login(self.sender, self.sender_p.decode())
        s.sendmail(self.sender, self.receiver, message)
        s.quit()

    def send_ontrack_msg(self, message, update_count):
        line = 'task update' if update_count == 1 else 'task updates'
        subject = '{} Ontrack {}!'.format(update_count, line)
        email = 'Subject: {}\n\n{}\n'.format(subject, message)
        self.send_email(email)