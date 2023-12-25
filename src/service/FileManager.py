import base64
import json
from pathlib import Path
from src.utils import HTML
from src.protocol import HTTP


class File_Manager:
    def __init__(self, base_path):
        self.title = "File Manager: "
        self.base_path = Path(base_path)
        self.USERS_DB = self.load_user_db()
        self.render = HTML.html_render("templates", "template.html")

    def load_user_db(self):
        accounts_path = self.base_path / 'src' / 'service' / 'accounts.json'
        try:
            with accounts_path.open('r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def authorize(self, auth_header, ret_username):
        if auth_header is None:
            return False
        if not auth_header.startswith('Basic '):
            return False
        encoded_credentials = auth_header.split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
        if username in self.USERS_DB:
            if self.USERS_DB[username] == password:
                ret_username[0] = username
                print("Logged in")
                return True
            else:
                return False
        else:
            return False

    def process(self, data):
        request = HTTP.parse_request(data)
        print(request)
        headers = {}

        try:
            username = ['']
            auth_header = request.header.fields.get('Authorization')
            if auth_header and self.authorize(auth_header, username):
                pass
            else:
                out = self.render.make_login()
                headers['Content-Type'] = 'text/html'
                headers['Content-Length'] = str(len(out))
                headers['WWW-Authenticate'] = 'Basic realm="Authorization Required"'
                return HTTP.build_response(401, 'Unauthorized', headers, out)

            dir_path = self.base_path / 'data' / username[0]
            if not dir_path.exists():
                dir_path.mkdir()

            if request.url.strip('/') == 'favicon.ico':
                file_path = self.base_path / 'data' / request.url.strip('/')
            elif request.url.strip('/') == '':
                file_path = dir_path
            else:
                file_path = dir_path / request.url.strip('/')
            print(file_path)
            if request.method == 'GET':
                if file_path.is_dir():
                    files_and_dirs = list(file_path.iterdir())
                    formatted_list = [{"path": '/' + f.name, "name": f.name} for f in files_and_dirs]
                    out = self.render.make_main_page(self.title + username[0], formatted_list)
                    headers['Content-Type'] = 'text/html'
                    headers['Content-Length'] = str(len(out))
                    return HTTP.build_response(200, 'OK', headers, out)
                elif file_path.is_file():
                    with file_path.open('rb') as file:
                        file_content = file.read()
                    content_type = 'application/octet-stream'
                    content_disposition = f'attachment; filename="{file_path.name}"'
                    if file_path.name.endswith('favicon.ico'):
                        content_type = 'image/x-icon'
                    headers['Content-Type'] = content_type
                    headers['Content-Length'] = str(len(file_content))
                    headers['Content-Disposition'] = content_disposition
                    return HTTP.build_response(200, 'OK', headers), file_content
                else:
                    return HTTP.build_response(404, 'Not Found', headers, 'File Not Found')

            elif request.method == 'POST':
                post_type = request.header.fields.get('Post-Type')
                if post_type == 'Upload':
                    with file_path.open('w') as file:
                        file.write(request.body)
                    return HTTP.build_response(200, 'OK', headers, 'File Saved')
                elif post_type == 'Delete':
                    if file_path.exists():
                        file_path.unlink()
                        return HTTP.build_response(200, 'OK', headers, 'File Deleted')
                    else:
                        return HTTP.build_response(404, 'Not Found', headers, 'File Not Found')
                else:
                    return HTTP.build_response(400, 'Bad Request', headers, 'Bad Request')

            else:
                return HTTP.build_response(405, 'Method Not Allowed', headers, 'Method Not Allowed')

        except Exception as e:
            return HTTP.build_response(500, 'Internal Server Error', headers, str(e))
