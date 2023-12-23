import os
import base64
import json
from utils import html
from protocol import http

class File_Manager:
    def __init__(self):
        self.title = "Py File Manager"
        self.username = None;
        self.USERS_DB = self.load_user_db()


    def load_user_db(self):
        try:
            with open('accounts.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {} 
        

    def authorize(self, auth_header):
        if auth_header is None:
            return False
        if not auth_header.startswith('Basic '):
            return False
        encoded_credentials = auth_header.split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
        if not auth_header or not auth_header.startswith('Basic '):
            return False
        if username in self.USERS_DB:
            if self.USERS_DB[username] == password:
                self.username = username
                return True
            else:
                return False
        else:
            return False


    def process(self, data):
        try:
            request = http.parse_request(data)
            print(request.method)
            print(request.url)
            print(request.header)
            print(request.body)

            render = html.html_render("./templates", "template.html")

            if self.username is None:
                print("Not loginned")
                if self.authorize(request.header.fields.get('Authorization')):
                    out = render.make_main_page(self.title, os.listdir('../../data/'+self.username))
                    return http.build_response(200, 'OK', {'Content-Type': 'text/html'}, out)
                else:
                    out = render.make_login()
                    headers = {'Content-Type': 'text/plain', 'WWW-Authenticate': 'Basic realm="Authorization Required"'}
                    return http.build_response(401, 'Unauthorized', headers, out)

            if request.method == 'GET':
                file_path = '../../data/'+request.url.strip('/')
                print(file_path)
                if request.url.strip('/') == '':
                    file_path = '../../data'+self.username
                if request.url.split('/')[0] != self.username:
                    return http.build_response(403, 'Forbidden', {'Content-Type': 'text/plain'}, 'Forbidden')
                # dir
                if os.path.isdir(file_path):
                    out = render.make_main_page(self.title, os.listdir(file_path))
                    return http.build_response(200, 'OK', headers, out)

                # file
                if os.path.isfile(file_path):
                    with open(file_path, 'r') as file:
                        file_content = file.read()
                    headers = {'Content-Type': 'text/plain'}
                    return http.build_response(200, 'OK', headers, file_content)

                else:
                    headers = {'Content-Type': 'text/plain'}
                    return http.build_response(404, 'Not Found', headers, 'File Not Found')

            elif request.method == 'POST':
                if request.header.fields.get('Post-Type') == 'Upload':
                    file_path = request.url.strip('/')
                    with open(file_path, 'w') as file:
                        file.write(request.body)
                    headers = {'Content-Type': 'text/plain'}
                    return http.build_response(200, 'OK', headers, 'File Saved')
                elif request.header.fields.get('Post-Type') == 'Delete':
                    file_path = request.url.strip('/')
                    os.remove(file_path)
                    headers = {'Content-Type': 'text/plain'}
                    return http.build_response(200, 'OK', headers, 'File Deleted')
                else:
                    headers = {'Content-Type': 'text/plain'}
                    return http.build_response(400, 'Bad Request', headers, 'Bad Request')
            else:
                headers = {'Content-Type': 'text/plain'}
                return http.build_response(405, 'Method Not Allowed', headers, 'Method Not Allowed')
        except Exception as e:
            headers = {'Content-Type': 'text/plain'}
            return http.build_response(500, 'Internal Server Error', headers, str(e))
