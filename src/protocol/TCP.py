import socket


class TCPServer:
    def __init__(self, host, port, thread_pool, file_manager):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.thread_pool = thread_pool
        self.file_manager = file_manager
        self.running = True

    def handle_client(self, client_socket):
        client_socket.settimeout(5.0)
        with client_socket:
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    send_message = self.file_manager.process(data.decode())
                    if type(send_message) is tuple:
                        client_socket.send(send_message[0].encode())
                        client_socket.send(send_message[1])
                        # print(f"we send response: {send_message[0].encode()}, raw body size: {len(send_message[1])}")
                    else:
                        client_socket.send(send_message.encode())
                        # print(f"we send response: {send_message.encode()}")
                except socket.timeout:
                    print("socket timeout, close")
                    break
        print("Connection closed")

    def run(self):
        while self.running:
            # try:
            client_socket, addr = self.server_socket.accept()
            # except OSError:
            #     break
            print(f"Connected to {addr}")
            self.thread_pool.submit(lambda: self.handle_client(client_socket))

    def stop(self):
        self.running = False
        print("tcp server stop")
        socket
        self.server_socket.close()
        self.thread_pool.stop()
