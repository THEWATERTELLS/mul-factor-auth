import sqlite3
from bcrypt import hashpw, gensalt

class AdminSys:
    def __init__(self):
        self.conn = sqlite3.connect('data/database.db')
        self.c = self.conn.cursor()
        
    def get_user_info(self, username):
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        return self.c.fetchone()
    
    def get_all_users(self):
        self.c.execute("SELECT * FROM users")
        return self.c.fetchall()
    
    def register_user(self, username, password, public_key, device_id):
        self.c.execute("INSERT INTO users (username, password_hash, public_key, device_id) VALUES (?, ?, ?, ?)", (username, password, public_key, device_id))
        self.conn.commit()

    def start(self):
        print("hello, Admin!")
        while True:
            print("select option:")
            print("1. get all users")
            print("2. get user info")
            print("3. register user")
            print("4. exit")
            option = input()
            if option == "1":
                print(self.get_all_users())
            
            elif option == "2":
                username = input("Enter username: ")
                print(self.get_user_info(username))
            
            elif option == "3":
                username = input("Enter username: ")
                if self.get_user_info(username):
                    print("User already exists")
                    continue
                password = input("Enter password: ")
                re_password = input("Re-enter password: ")
                if password != re_password:
                    print("Passwords do not match")
                    continue
                password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
                public_key_pem = input("Enter public key pem url: ")
                public_key = open(public_key_pem).read()
                device_id = input("Enter device id: ")
                self.register_user(username, password_hash, public_key, device_id)
            elif option == "4":
                break
            else:
                print("Invalid option")