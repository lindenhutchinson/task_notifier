from cryptography.fernet import Fernet

class PasswordManager:
    @staticmethod
    def make_key():
        return PasswordManager.ensure_as_str(Fernet.generate_key())

    @staticmethod
    def encrypt(key, password):
        key = PasswordManager.ensure_as_bytes(key)
        password = PasswordManager.ensure_as_bytes(password)
        return PasswordManager.ensure_as_str(Fernet(key).encrypt(password))

    @staticmethod
    def decrypt(key, password):
        key = PasswordManager.ensure_as_bytes(key)
        password = PasswordManager.ensure_as_bytes(password)
        return PasswordManager.ensure_as_str(Fernet(key).decrypt(password))

    @staticmethod
    def ensure_as_bytes(content):
        return content.encode("utf-8")

    @staticmethod
    def ensure_as_str(content):
        return str(content).strip("b' '")

# if __name__ == "__main__":


