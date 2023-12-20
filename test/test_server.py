import socket
import threading
import time
from src.protocol import tcp
from src.protocol import http
from src.utils import html

# 测试服务器功能


def test_server():
    server = tcp.TCP_Server('127.0.0.1', 65432)

    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    time.sleep(1)


    while True:
        # input_message = input("Input message: ")
        # if (input_message == 'exit'):
        #     break
        # time.sleep(1)
        received_message = server.recv()
        print("client request: ", received_message)
        render = html.html_render("/home/lambillda/2023fall/Network305/SUSTech-CS305-Project/src/templates", "template.html")
        title = "foo"
        files = [{"path": "p1", "name": "n1"}, {"path": "p2", "name": "n2"}]
        out = render.make_html(title, files)
        eg_fields = {}
        eg_fields["Content-Type"] = "text/html"
        eg_fields["Content-Length"] = len(out)
        tmt=input("pass key to continue")
        # eg_fields["Keep-Alive"] = "timeout=1, max=100"
        time.sleep(1)
        packet = http.build_response(200, 'OK', eg_fields, out)
        server.send(packet.to_raw_data())
        print(f"we send response: {packet.to_raw_data()}")


    server.stop()
    server_thread.join()


# 运行测试
if __name__ == "__main__":
    test_server()
