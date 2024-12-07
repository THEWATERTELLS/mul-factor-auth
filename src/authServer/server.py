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

CURRENT_LOCATION = (104.00, 30.56) # Sichuan University, Chengdu, China

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
            
            otp = self.gen_otp()
            enc_otp = self.enc_otp_with_pkey(otp, pkey_str)

            time_start = time.time()
            conn.sendall(enc_otp.encode())

            conn.close()
            return username, otp, time_start
        
        except Exception as e:
            print(e)
            return None, None
            
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
        return otp
        
    def get_user_info(self, username):
        try:
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT public_key FROM users WHERE username = ?", (username,))
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

        for _ in range(5):

            if input_otp == correct_otp and time.time() - time_start < 120:
                if checkpw(password.encode('utf-8'), pw_hash.encode('utf-8')):
                    
                    return True
                    
                else: 
                    print("Incorrect password")
                    continue    
            else:
                print("Incorrect OTP or OTP expired")
                continue

        return False
    

    def start(self):
        print("Server started")
        while True:
            conn, addr = self.accept_connection()
            username, otp, time_start = self.handler(conn, addr)

            input_username = input("Enter username: ")
            input_password = input("Enter password: ")
            input_otp = input("Enter OTP: ")

            if self.log_in(input_username, input_password, input_otp, otp, time_start):
                print("Login successful!")
            else:
                print("Login failed!")


            

        
                