import socket
import sys

HOST = "127.0.0.1"
PORT = 65433

message = sys.argv[1]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))

    client.send(message.encode())