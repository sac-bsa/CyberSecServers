#!/usr/bin/python3
host = "mackgregory.ml"
port = 4003

import socket

def add(data):
    try:
        a, _, b = data.split()
        return str(int(a) + int(b))
    except Exception as e:
        print(data)
        raise e 
sock = socket.create_connection((host, port))
d = sock.recv(65).decode()
print(d)
for _ in range(10):
    data_bytes = sock.recv(4096)
    data_str   = data_bytes.decode()
    value = add(data_str)
    value_str = str(value)
    print(data_str.strip(), "=", value_str)
    value_bytes = value_str.encode()
    sock.send(value_bytes)
d = sock.recv(4096).decode()
print(d)
sock.close()
