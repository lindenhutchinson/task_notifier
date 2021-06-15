from tools.password_manager import PasswordManager
import os

if __name__ == "__main__":
    key = PasswordManager.make_key()
    username=input("Enter your ontrack username (your deakin email without the @deakin.edu.au):\n")
    password=input("Enter your deakin password:\n")
    os.system('cls')
    e_pass = PasswordManager.encrypt(key, password)
    with open(".env", "w") as fn:
        fn.write(f"KEY={key}\n")
        fn.write(f"USER={username}\n")
        fn.write(f"PASS={e_pass}\n")
        fn.write("WEBHOOK=<Your-Webhook-Url-Here>")
    print("Created .env file")