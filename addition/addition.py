import socket
import selectors
import types
import random
import datetime

### PARAMS
a = 100
b = 200
problems = 10
time = 10


host="0.0.0.0"
port = 4003

chars = "1234567890_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
random.seed(4003)
flag = [random.choice(chars) for _ in range(32)]
flag = ("DCyberSec_{" + "".join(flag) + "}").encode("utf-8")
random.seed()

class Adder:
    def __init__(self):
        self.remaining = problems
        self.time_start = datetime.datetime.now()
        self.curr = (random.randint(a, b), random.randint(a, b))
        self.answer = self.curr[0] + self.curr[1]
        self.stop = False

    def cont(self, inb):
        if (datetime.datetime.now() - self.time_start).seconds > time:
            self.stop = True
            return "You were too slow, I failed\n".encode("utf-8")
        try:
            if self.answer != int(inb.decode("utf-8").strip()):
                self.stop = True
                return "That wasn't even right!\n".encode("utf-8")
        except:
            self.stop = True
            return "That wasn't even a number!\n".encode("utf-8")
        self.remaining -= 1
        if self.remaining == 0:
            self.stop = True
            return flag
        self.curr = (random.randint(a, b), random.randint(a, b))
        self.answer = self.curr[0] + self.curr[1]
        return (str(self.curr[0]) + " + " + str(self.curr[1]) + "\n").encode("utf-8")

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
    adder = Adder()
    data = types.SimpleNamespace(addr=addr, inb=b'',
            outb=("I need some help with my math homework, but you need to be quick\n" + str(adder.curr[0]) + " + " + str(adder.curr[1])).encode("utf-8"), adder=adder)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    try:
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                data.outb = data.adder.cont(recv_data)
                while data.outb:
                    sent = sock.send(data.outb)
                    data.outb = data.outb[sent:]
                if data.adder.stop:
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
    except:
        print("Error on", data.addr)
        sel.unregister(sock)
        sock.close()

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)
