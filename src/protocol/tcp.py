import socket
import threading


class TCP_Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn = None
        self.addr = None

    def start(self):
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()

    def stop(self):
        if self.conn:
            self.conn.close()
        self.sock.close()

    def recv(self) -> str:
        while not self.conn:
            pass
        return self.conn.recv(1024).decode()

    def send(self, msg):
        if self.conn:
            try:
                self.conn.send(msg)
            except BrokenPipeError:
                print("Connection broken. Unable to send message.")

    def send_with_attach(self, msg, at):
        if self.conn:
            try:
                self.conn.send(msg)
                self.conn.send(at)
            except BrokenPipeError:
                print("Connection broken. Unable to send message.")
