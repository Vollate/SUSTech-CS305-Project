import socket
import threading
import time
from protocol import tcp

# 测试服务器功能
def test_server():
    # 创建服务器实例
    server = tcp.TCP_Server('127.0.0.1', 65432)
    
    # 在一个新线程中启动服务器
    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    # 等待服务器启动
    time.sleep(1)

    # 创建客户端并连接到服务器
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 65432))

    # 发送和接收消息
    test_message = "Hello, Server!"
    client.sendall(test_message.encode())
    time.sleep(1)
    received_message = server.recv()
    print(f"Received from server: {received_message}")

    # 关闭客户端和服务器
    client.close()
    server.stop()
    server_thread.join()

# 运行测试
if __name__ == "__main__":
    test_server()
