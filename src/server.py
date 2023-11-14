from protocal import tcp
from protocal import http
from service import file_manager
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, help='ip address')
parser.add_argument('-p', type=int, help='port')
argv = parser.parse_args()

if __name__ == '__main__':
    tcp_server = tcp.TCP_Server(argv.i, argv.p)
    manager = file_manager.File_Manager(tcp_server)
    tcp_server.start()
    while True:
        data = tcp_server.recv()
        manager.process(http.parse(data))
