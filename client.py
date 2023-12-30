import argparse
import socket
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from Cryptodome.Cipher import AES
import os
import uuid
import base64


class Client:
    def __init__(self, key, conn):
        self.key = key
        self.conn = conn
        self.cipher = AES.new(key, AES.MODE_EAX)

    def send_get(self, file_path):
        msg = f"GET {file_path} HTTP/1.1\r\nAuthorization: Basic MTIzOjEyMw==\r\nContent-Length: 0\r\n\r\n\r\n\r\n"
        print(f"send get msg:\n{msg}")
        self.conn.send(self.encrypt_msg(msg).encode())

    def send_post(self, local_path, file_path):
        with open(local_path, "rb") as f:
            data = f.read()
        boundary = "----WebKitFormBoundary" + str(uuid.uuid4()).replace("-", "")
        body = (
            (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(local_path)}"\r\n'
                f"Content-Type: application/octet-stream\r\n\r\n"
            ).encode()
            + data
            + f"\r\n--{boundary}--\r\n".encode()
        )
        msg = f"POST /upload?path={file_path}\n HTTP/1.1\r\nContent-Length: {len(body)}\r\nContent-Type=multipart/form-data; boundary={boundary}\r\n\r\n"
        self.conn.send(self.encrypt_msg(msg))

    def handle_input(self):
        while True:
            self.send_get(input("URL path:\n>> "))
            receive_data = self.conn.recv(102400)
            print(self.decrypt_msg(receive_data).decode())
            continue
            cmd = input("GET|POST|exit\n>> ")
            if cmd == "exit":
                return
            elif cmd == "GET":
                self.send_get(input("URL path:\n>> "))
            elif cmd == "POST":
                local_path = input("Local file path:\n>> ")
                server_path = input("Server directory path:\n>> ")
                self.send_post(local_path, server_path)
            else:
                print("Invalid input")
                continue
            receive_data = self.conn.recv(102400).decode
            print(self.dencrypt_msg(receive_data))

    def encrypt_msg(self, msg):
        encrypted_msg, tag = self.cipher.encrypt_and_digest(msg.encode())
        return "&".join(
            [
                base64.b64encode(x).decode()
                for x in (self.cipher.nonce, tag, encrypted_msg)
            ]
        )

    def decrypt_msg(self, msg):
        nonce, tag, ciphertext = [base64.b64decode(x) for x in msg.decode().split("&")]
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)


parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, help="ip address")
parser.add_argument("-p", type=int, help="port")
argv = parser.parse_args()

client_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_conn.connect((argv.i, argv.p))
public_key_pem = client_conn.recv(1024)
public_key = load_pem_public_key(public_key_pem)
key = os.urandom(32)
encrypted_symmetric_key = public_key.encrypt(
    key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
client_conn.send(encrypted_symmetric_key)
cipher = AES.new(key, AES.MODE_EAX)
client = Client(key, client_conn)
client.handle_input()
