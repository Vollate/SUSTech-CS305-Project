import os
import base64
import json
from src.utils import html
from src.protocol import http

class File_Manager:
    def __init__(self, base_path):
        self.title = "File Manager: "
        self.base_path = base_path
        self.username = None
        self.USERS_DB = self.load_user_db()
        self.render = html.html_render("templates", "template.html")


    def load_user_db(self):
        accounts_path = os.path.join(self.base_path,'src','service', 'accounts.json')
        try:
            with open(accounts_path, 'r') as file:
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
        if username in self.USERS_DB:
            if self.USERS_DB[username] == password:
                self.username = username
                print("loginned")
                return True
            else:
                return False
        else:
            return False


    def process(self, data):
        request = http.parse_request(data)
        print(request)
        headers = {}

        try:
            if self.username is None:
                print("Not loginned")
                auth_header=request.header.fields.get('Authorization')
                if auth_header is not None:
                    if self.authorize(request.header.fields.get('Authorization')):
                        pass
                    else:
                        out = self.render.make_login()
                        headers['Content-Type'] = 'text/html'
                        headers['Content-Length'] = len(out)
                        headers['WWW-Authenticate'] = 'Basic realm="Authorization Required"'
                        return http.build_response(401, 'Unauthorized', headers, out)
                        
                    dir_path = os.path.join(self.base_path,'data',self.username)
                    files_and_dirs = os.listdir(dir_path)
                    formatted_list = [{"path": os.path.join(dir_path, file_or_dir), "name": file_or_dir} for file_or_dir in files_and_dirs]
                    out = self.render.make_main_page(self.title+self.username, formatted_list)
                    headers['Content-Type'] = 'text/html'
                    headers['Content-Length'] = len(out)
                    return http.build_response(200, 'OK', headers, out)
                else:
                    out = self.render.make_login()
                    headers['Content-Type'] = 'text/html'
                    headers['Content-Length'] = len(out)
                    headers['WWW-Authenticate'] = 'Basic realm="Authorization Required"'
                    return http.build_response(401, 'Unauthorized', headers, out)

            file_path = os.path.join(self.base_path,'data',request.url.strip('/'))
            if request.url.strip('/') == '':
                file_path = os.path.join(self.base_path,'data',self.username)
            if request.url.split('/')[0] != self.username and request.url.strip('/') != 'favicon.ico':
                return http.build_response(403, 'Forbidden', headers, '')

            if request.method == 'GET':
                # dir
                if os.path.isdir(file_path):
                    files_and_dirs = os.listdir(dir_path)
                    formatted_list = [{"path": os.path.join(dir_path, file_or_dir), "name": file_or_dir} for file_or_dir in files_and_dirs]
                    out = self.render.make_main_page(self.title+self.username, formatted_list)
                    headers['Content-Type'] = 'text/html'
                    headers['Content-Length'] = len(out)
                    return http.build_response(200, 'OK', headers, out)

                # file
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as file:
                        file_content = file.read()
                    content_type = 'application/octet-stream'
                    content_disposition = f'attachment; filename="{os.path.basename(file_path)}"'

                    if file_path.endswith('favicon.ico'):
                        content_type = 'image/x-icon'
                        content_disposition = 'inline'

                    headers['Content-Type'] = content_type
                    headers['Content-Length'] = len(file_content)
                    headers['Content-Disposition'] = content_disposition

                    return http.build_response(200, 'OK', headers, file_content)

                else:
                    headers['Content-Type'] = 'text/plain'
                    return http.build_response(404, 'Not Found', headers, 'File Not Found')

            elif request.method == 'POST':

                if request.header.fields.get('Post-Type') == 'Upload':
                    with open(file_path, 'w') as file:
                        file.write(request.body)
                    headers['Content-Type'] = 'text/plain'
                    return http.build_response(200, 'OK', headers, 'File Saved')
                elif request.header.fields.get('Post-Type') == 'Delete':
                    os.remove(file_path)
                    headers['Content-Type'] = 'text/plain'
                    return http.build_response(200, 'OK', headers, 'File Deleted')
                else:
                    headers['Content-Type'] = 'text/plain'
                    return http.build_response(400, 'Bad Request', headers, 'Bad Request')
            else:
                headers['Content-Type'] = 'text/plain'
                return http.build_response(405, 'Method Not Allowed', headers, 'Method Not Allowed')

        except Exception as e:
            headers['Content-Type'] = 'text/plain'
            return http.build_response(500, 'Internal Server Error', headers, str(e))
