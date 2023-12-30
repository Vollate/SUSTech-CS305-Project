from src.protocol import TCP
from src.service import FileManager
from pathlib import Path
import signal
import argparse
from src.service import ThreadPool

# just for dev
import subprocess
import platform

parser = argparse.ArgumentParser()
parser.add_argument("-i", type=str, help="ip address")
parser.add_argument("-p", type=int, help="port")
parser.add_argument("-e", type=bool, default=False, help="enable encryption")
argv = parser.parse_args()

base_path = Path(__file__).resolve().parent
fm = FileManager.File_Manager(base_path)
tcp_server = TCP.TCPServer(argv.i, argv.p, ThreadPool.ThreadPool(1000), fm, argv.e)


def signal_handler(sig, frame):
    tcp_server.stop()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print("server start")
    if platform.platform().startswith("Linux"):
        subprocess.call(["xdg-open", "127.0.0.1:{}".format(argv.p)])
    tcp_server.run()
