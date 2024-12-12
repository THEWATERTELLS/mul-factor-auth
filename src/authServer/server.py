import socket
import sqlite3
import os
import random 
import string
import time
from bcrypt import checkpw
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64
from adminSys import AdminSys

CURRENT_LOCATION = (104.00, 30.56) # Sichuan University, Chengdu, China
TIME_START = 1733000000

class Server:
    
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port

        self.socket = self._init_socket()

    def _init_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen()
        print(f"Listening on {self.host}:{self.port}")
        return s
    
    def accept_connection(self):
        conn, addr = self.socket.accept()
        print('Connected by', addr)
        return conn, addr
    
    def handler(self, conn, addr):
        try:
            
            data = conn.recv(1024).decode()
            # print(f"Received: {data}")
            username, location = self.parse_username_and_location(data)
            verify = self.verify_user(username, location)
            pkey_str = self.get_user_info(username)[3]
            
            if not verify:
                conn.sendall(b"Invalid")
                conn.close()
                return None, None, None
            
            otp = self.gen_otp()
            enc_otp = self.enc_otp_with_pkey(otp, pkey_str)

            time_start = time.time()
            conn.sendall(enc_otp.encode())
            print(f"Sent encrypted OTP")
            # print(f"encrypted OTP: {enc_otp}")
            # print(f"Sent OTP: {otp}")
            # time.sleep(3)

            conn.close()
            print("connection closed")
            return username, otp, time_start
        
        except Exception as e:
            print(f"error in handler, error: {e}")
            return None, None, None
            
    def enc_otp_with_pkey(self, otp, pkey):
        pkey = load_pem_public_key(pkey.encode('utf-8'))
        encrypted = pkey.encrypt(
            otp.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted).decode('utf-8')

    def parse_username_and_location(self, data):
        username = data.split(',')[0]
        parts = data.split(',')[1].split(':')
        location = (float(parts[0]), float(parts[1]))
        return username,location

    def gen_otp(self):
        characters = string.ascii_letters + string.digits
        otp = ''.join(random.choices(characters, k=6))
        # print(f"generated otp: {otp}")
        return otp
        
    def get_user_info(self, username):
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if not user:
                return None
            
            return user
        
        except Exception as e:
            print(e)
            return None
        
    def verify_user(self, username, location):
        try:
            user = self.get_user_info(username)
            if user is None:
                return False
            
            server_location = CURRENT_LOCATION
            if abs(server_location[0] - location[0]) > 0.1 or abs(server_location[1] - location[1]) > 0.1:
                return False
            
            return True
        
        except Exception as e:
            print(e)
            return False

    def log_in(self, username, password, input_otp, correct_otp, time_start):
        
        user_info = self.get_user_info(username)
        pw_hash = user_info[2]

        if input_otp == correct_otp and time.time() - time_start < 120:
            if checkpw(password.encode('utf-8'), pw_hash.encode('utf-8')):
                return True 
            else: 
                print("Incorrect password")
        else:
            print("Incorrect OTP or OTP expired")

        return False
    
    def check_user_failure(self, username):
        conn = sqlite3.connect('data/database.db')
        c = conn.cursor()
        c.execute("SELECT login_fail_time FROM failure WHERE username = ?", (username,))
        try:
            fail_time = c.fetchone()[0]
        except:
            fail_time = None
        conn.close()
        if fail_time is None:
            return False
        if int(time.time() - TIME_START) - fail_time < 60:
            return True
        return False

    def record_user_failure(self, username):
        conn = sqlite3.connect('data/database.db')
        c = conn.cursor()
        c.execute("UPDATE failure SET login_fail_time = ? WHERE username = ?", (int(time.time() - TIME_START), username))
        conn.commit()
        conn.close()

    def start(self):
        while True:
            print("Server started")
            conn, addr = self.accept_connection()
            username, otp, time_start = self.handler(conn, addr)
            for i in range(5):
                input_username = input("Enter username: ")
                if input_username != username:
                    print("You are not the requesting user!")
                    continue
                if self.check_user_failure(username):
                    print("you are prohibitted from logging in")
                    break

                input_password = input("Enter password: ")
                input_otp = input("Enter OTP: ")

                if self.log_in(input_username, input_password, input_otp, otp, time_start):
                    print("Login successful!")
                    if username == 'admin':
                        admin_sys = AdminSys()
                        admin_sys.start()
                    else:
                        print(f"Welcome, {username}!")
                else:
                    print("Login failed! wait 1 minute to try again")
                    break
            self.record_user_failure(username)

server = Server()
server.start() 