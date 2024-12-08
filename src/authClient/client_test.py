import socket
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64

HOST = '127.0.0.1'
PORT = 12345
# this is the token device written in python.
# only for test, the real token project is written in swift as an Xcode project.
# uses private key of admin.

with open("src/adminSK.pem", 'r') as f:
    admin_sk = f.read()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"connected to {HOST}:{PORT}")

    s.sendall(b"admin,104.00:30.56")
    enc_otp = s.recv(1024)
    encrypted_data = base64.b64decode(enc_otp)

    private_key = serialization.load_pem_private_key(
        admin_sk.encode('utf-8'),
        password=None,
    )

    otp = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode('utf-8')

    print(f"decrypted OTP: {otp}")
    # print(f"received {enc_otp}")



