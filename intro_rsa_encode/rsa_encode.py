import socket
import selectors
import types
import random
host="0.0.0.0"
port = 4001
p_primes = [3, 7, 13]
q_primes = [17, 19, 23]
e = 5
chars = "1234567890_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
random.seed(43)
flag = [random.choice(chars) for _ in range(32)]
flag = ("DCyberSec_{" + "".join(flag) + "}").encode("utf-8")
random.seed()
def rsa_example():
    # We will generate primes
    p = random.choice(p_primes)
    q = random.choice(q_primes)
    n = p * q
    m = random.randint(2,n-1)
    encrypted = pow(m, e, n)
    out = "I want to send a message, can you encrypt " + str(m) + "?\n" 
    out += "(n, e) = (" + str(n) + ", " + str(e) + ").\n"
    return (out, encrypted)

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
    rsa = rsa_example()
    data = types.SimpleNamespace(addr=addr, inb=b'',
            outb=rsa[0].encode("utf-8"), m=rsa[1])
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            message = recv_data.decode("utf-8")
            if data.m == int(message):
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
