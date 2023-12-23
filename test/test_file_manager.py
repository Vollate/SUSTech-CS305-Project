import os
from protocol import http
from server import file_manager
import requests

class Test_File_Manager:
    def setup(self):
        self.file_manager = file_manager.File_Manager(None)

    def test_process_get(self):
        # 目标 URL
        url = "http://localhost:8080/data"

        # 创建一个 Request 对象
        req = requests.Request('GET', url)
        prepared = req.prepare()

        # 手动构建原始 HTTP 请求文本
        request_text = f"{prepared.method} {prepared.url} HTTP/1.1\r\n"
        request_text += "\r\n".join(f"{k}: {v}" for k, v in prepared.headers.items())
        request_text += "\r\n\r\n"

        response = self.file_manager.process(request_text)
        print(response)

if __name__ == "__main__":
    test_file_manager = Test_File_Manager()
    test_file_manager.setup()
    test_file_manager.test_process_get()
    