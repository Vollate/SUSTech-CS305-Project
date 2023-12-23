from protocol import tcp
from protocol import http
from service import file_manager
import signal
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, help="ip address")
parser.add_argument("-p", type=int, help="port")
argv = parser.parse_args()

def signal_handler(sig, frame, server):
    print("  Ctrl+C detected, shutting down the server...")
    server.stop()
    exit(0)

if __name__ == "__main__":
    server = tcp.TCP_Server(argv.i, argv.p) #这个tcpserver要考虑一下多客户端的情况
    fm = file_manager.File_Manager()
    server.start()
    time.sleep(1)
    # Signal handler
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, server))
    print("server start")

    while True:
        try:
            received_message = server.recv()
            print("==================================")
            print("client request: ", received_message)
            input("pass any key to continue")
            server.send(fm.process(received_message).to_raw_data())
            print(f"we send response: {fm.process(received_message).to_raw_data()}")
        except Exception as e:
            print("An error occurred:", e)
