import os
from protocol import http

class File_Manager:
    def __init__(self, tcp_server):
        self.server = tcp_server

    def process(self, data):
        try:

            request = http.parse_request(data)
            print(request.method)
            print(request.url)
            print(request.header)
            print(request.body)

            if request.method == 'GET':
                file_path = request.url.strip('/')
                print(file_path)
                # 如果是文件夹，列出文件夹内容
                if os.path.isdir(file_path):
                    file_list = os.listdir(file_path)
                    headers = {'Content-Type': 'text/plain'}
                    with open('template.html', 'r') as file:
                        template = file.read()
                    html = template.replace('{title}', file_path).replace('{content}', '<br>'.join(file_list))
                    return http.build_response(200, 'OK', headers, html)

                if os.path.isfile(file_path):
                    with open(file_path, 'r') as file:
                        file_content = file.read()
                    headers = {'Content-Type': 'text/plain'}
                    return http.build_response(200, 'OK', headers, file_content)

                else:
                    headers = {'Content-Type': 'text/plain'}
                    return http.build_response(404, 'Not Found', headers, 'File Not Found')

            elif request.method == 'POST':
                file_path = request.url.strip('/')
                with open(file_path, 'w') as file:
                    file.write(request.body)
                headers = {'Content-Type': 'text/plain'}
                return http.build_response(200, 'OK', headers, 'File Saved')

            else:
                headers = {'Content-Type': 'text/plain'}
                return http.build_response(405, 'Method Not Allowed', headers, 'Method Not Allowed')
        except Exception as e:
            headers = {'Content-Type': 'text/plain'}
            return http.build_response(500, 'Internal Server Error', headers, str(e))
