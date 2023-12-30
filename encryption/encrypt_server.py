from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from Cryptodome.Cipher import AES
import socket
import base64

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 5555))
server.listen(1)
print("Server listening on port 5555")

conn, addr = server.accept()
print(f"Connection from {addr}")

conn.send(pem)

encrypted_symmetric_key = conn.recv(1024)

symmetric_key = private_key.decrypt(
    encrypted_symmetric_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)

encrypted_message = conn.recv(4096)
nonce, tag, ciphertext = [
    base64.b64decode(x) for x in encrypted_message.decode().split("|")
]
cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=nonce)
decrypted_message = cipher.decrypt_and_verify(ciphertext, tag)
print("Decrypted message:", decrypted_message.decode())

conn.close()
