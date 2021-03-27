import socket
import json

d = {"username":"ubuntu","ip":"10.1.1.86","port":"51510"}
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('0.0.0.0', 7007))
client.send(json.dumps(d).encode('UTF-8'))
from_server = client.recv(4096)
client.close()

print(from_server)  