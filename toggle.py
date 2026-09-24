import socket
from configs.settings import VOICEFLOW_PORT

HOST = "127.0.0.1"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, VOICEFLOW_PORT))
