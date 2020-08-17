from cryptography.fernet import Fernet

class PasswordManager:
    def __init__(self,p):
        self.p = p
        self.crypto = False

    def use_key(self, key):
        self.crypto = Fernet(key)

        
    # use this function to generate keys, then save them as a local file
    def make_key(self):
        key = Fernet.generate_key()
        self.use_key(key)
        return key

    # I use this to encrypt my passwords then store them as env variables
    def encrypt(self, password):
        if not self.crypto:
            print("You don't have a key so you won't be able to encrypt that password")
        return self.crypto.encrypt(password)

    # this function is used in the script to retrieve the plaintext password
    def decode(self):
        if not self.crypto:
            print("You don't have a key so you won't be able to decrypt that password")

        return str(self.crypto.decrypt(self.p)).strip("b' '")