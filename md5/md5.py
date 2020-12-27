import socket
import selectors
import types
import random
import hashlib

host="0.0.0.0"
port = 4002

chars = "1234567890_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
random.seed(44)
flag = [random.choice(chars) for _ in range(32)]
flag = ("DCyberSec_{" + "".join(flag) + "}").encode("utf-8")
random.seed()
def md5_example():
    # We will generate primes
    m ="".join([random.choice(chars) for _ in range(20)]).strip()
    md5 = hashlib.md5(m.encode("ascii"))
    hashed = md5.hexdigest().strip()
    out = "I need to hash this message '" + str(m)+  "' ?\n" 
    return (out, hashed)

sel = selectors.DefaultSelector()
# ...
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)



def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    prompt, answer = md5_example()
    data = types.SimpleNamespace(addr=addr, inb=b'',
            outb=prompt.encode("utf-8"), m=answer)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            message = recv_data.decode("utf-8")
            print("'", message, "'")
            if data.m.strip() == message.strip():
                data.outb = flag
            else:
                data.outb = ("It was actually " + str(data.m)).encode("utf-8")
            while data.outb:
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]
            print("Closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            # print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)
