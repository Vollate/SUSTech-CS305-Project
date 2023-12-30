from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from Cryptodome.Cipher import AES
import socket
import base64

from src.protocol import HTTP


def establish_encrypted_connection(socket_conn):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    socket_conn.send(pem)
    encrypted_symmetric_key = socket_conn.recv(1024)
    return private_key.decrypt(
        encrypted_symmetric_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def send_encrypted_message(key, socket_conn, msg):
    cipher = AES.new(key, AES.MODE_EAX)
    if type(msg) is tuple:
        for i in range(len(msg)):
            cipher_text, tag = cipher.encrypt_and_digest(msg[i])
            msg[i] = "&".join(
                [base64.b64encode(x).decode() for x in (cipher.nonce, tag, cipher_text)]
            )

        socket_conn.send(msg[0].encode())
        socket_conn.send(msg[1])
    else:
        cipher_text, tag = cipher.encrypt_and_digest(msg.encode())
        msg = "&".join(
            [base64.b64encode(x).decode() for x in (cipher.nonce, tag, cipher_text)]
        )
        socket_conn.send(msg.encode())


def send_msg(socket_conn, msg):
    if type(msg) is tuple:
        socket_conn.send(msg[0].encode())
        socket_conn.send(msg[1])
    else:
        socket_conn.send(msg.encode())


def decrypt_msg(key, msg):
    nonce, tag, ciphertext = [
        base64.b64decode(x) for x in msg.decode().split("&")
    ]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)


class TCPServer:
    def __init__(self, host, port, thread_pool, file_manager, encrypt_enable=False):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.thread_pool = thread_pool
        self.file_manager = file_manager
        self.encrypt_enable = encrypt_enable
        self.running = True

    def handle_client(self, client_socket):
        # client_socket.settimeout(1.0)
        status = HTTP.HTTPStatus()
        with client_socket:
            key = establish_encrypted_connection(client_socket) if self.encrypt_enable else None
            while not status.oneshot or status.receive_partially:
                data = client_socket.recv(10240000000)
                if not data:
                    break
                if self.encrypt_enable:
                    data = decrypt_msg(key, data)
                send_message = self.file_manager.process(client_socket, data, status)
                if send_message is None:
                    continue
                if self.encrypt_enable:
                    send_encrypted_message(key, client_socket, send_message)
                else:
                    send_msg(client_socket, send_message)
        print("Connection closed")

    def run(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
            except OSError:
                break
            print(f"Connected to {addr}")
            # self.handle_client(client_socket)
            self.thread_pool.submit(lambda: self.handle_client(client_socket))

    def stop(self):
        self.running = False
        print("tcp server stop")
        self.server_socket.close()
        self.thread_pool.stop()
