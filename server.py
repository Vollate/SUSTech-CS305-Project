from protocol import tcp
from service import file_manager
import os
import signal
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, help="ip address")
parser.add_argument("-p", type=int, help="port")
argv = parser.parse_args()
SERVER_STATUS = True

def signal_handler(sig, frame):
    global SERVER_STATUS
    print("Shutting down the server...")
    SERVER_STATUS = False

if __name__ == "__main__":
    server = tcp.TCP_Server(argv.i, argv.p) #这个tcpserver要考虑一下多客户端的情况
    base_path = os.path.dirname(os.path.abspath(__file__))
    fm = file_manager.File_Manager(base_path)
    server.start()
    time.sleep(1)
    # Signal handler
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # 处理终止
    print("server start")

    while SERVER_STATUS:
        try:
            received_message = server.recv()
            print("==================================")
            print("client request: ", received_message)
            # input("pass any key to continue")
            send_message = fm.process(received_message)
            server.send(send_message.to_raw_data())
            print(f"we send response: {send_message.to_raw_data()}")
        except Exception as e:
            print("An error occurred:", e)

    server.stop()
    print("Server stopped.")
