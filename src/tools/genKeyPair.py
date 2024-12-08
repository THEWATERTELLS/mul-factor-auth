from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import sqlite3

def generate_key_pair():

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    public_key = private_key.public_key()
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return public_key_pem, private_key_pem


def store_public_key(username, pkey):
    conn = sqlite3.connect("data/database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET public_key = ? WHERE username = ?", (pkey, username))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    public_key, private_key = generate_key_pair()
    print("Public Key:")
    print(public_key)
    print("Private Key:")
    print(private_key)
#     pkey = '''-----BEGIN PUBLIC KEY-----
# MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0WN2FQUhkEThGTGcI5Xx
# fwA+Swdehgs2O2AaLnm6rXCjebky5Bhr8pl+hioorMdI+R6RqZ2ozGJXWt6OF33A
# hIdnxI1NA07y+hYo7Ki/ya4bYgNFCmwNJqMX1rj5AZzat/z6d9CIUraRzGfi77wZ
# PUf5bzJFPB5KMb89UDRQtOF8Mrb/JyRghPee7grS8Afxt0HEadrxRSSgnfXxW9WD
# 6soSJ0BiGrnwsWZGsoWufZ/VXLuW90u9eGAharM+P5dGvHMM45cyvLk3X6qmgl4h
# PZKvhJVy6eAMA922H69ThOx7JKgEgOn1EzyrKOWEaBfAJD8Q5r75G1ImBgGD3eVK
# lwIDAQAB
# -----END PUBLIC KEY-----'''
#     print(pkey)
#     store_public_key("admin", pkey)
