import socket
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from Cryptodome.Cipher import AES
import os
import base64

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 5555))
print("Connected to server")

public_key_pem = client.recv(1024)
public_key = load_pem_public_key(public_key_pem)
symmetric_key = os.urandom(32)

encrypted_symmetric_key = public_key.encrypt(
    symmetric_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
client.send(encrypted_symmetric_key)

cipher = AES.new(symmetric_key, AES.MODE_EAX)
plaintext = b"Hello, secure world!"
ciphertext, tag = cipher.encrypt_and_digest(plaintext)
message = "|".join(
    [base64.b64encode(x).decode() for x in (cipher.nonce, tag, ciphertext)]
)
client.send(message.encode())

client.close()
