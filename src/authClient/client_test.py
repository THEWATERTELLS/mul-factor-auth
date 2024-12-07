import socket

HOST = '127.0.0.1'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"connected to {HOST}:{PORT}")

    s.sendall(b"admin,104.00:30.56")
    enc_otp = s.recv(1024).decode()
    print(f"received {enc_otp}")



