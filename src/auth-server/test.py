import socket

HOST = '0.0.0.0'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening on {HOST}:{PORT}")
    conn, addr = s.accept()
    with conn:
        
        print('Connected by', addr)
        data = conn.recv(1024)
        print(f"Received: {data.decode()}")

        if data.decode() == "hello":
            data = b"world"
            conn.sendall(data)

        print("Closing connection")
        
