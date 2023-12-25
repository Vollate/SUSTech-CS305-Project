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
                return True
            else:
                return False
        else:
            return False
    
    def find_relative_path_to_target_folder(self, path, target_folder_name):
        path = Path(path).resolve()
        original_path = path
        while path.name != target_folder_name:
            if path.name == 'data':
                return True, None
            if path.parent == path:
                return False, None
            path = path.parent
        relative_path = original_path.relative_to(path.parent)
        return False, relative_path

    def process(self, data):
        request = HTTP.parse_request(data)
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

            request.url = request.url.strip('/')
            dir_path = self.base_path / 'data'
            is_root = request.url == '' or request.url == username[0]
            if not (dir_path / username[0]).exists():
                (dir_path / username[0]).mkdir()

            if is_root:
                file_path = dir_path / username[0]
                relative_path = Path(username[0])
            else:
                file_path = dir_path / request.url
                is_forbidden, relative_path = self.find_relative_path_to_target_folder(file_path, username[0])
                if is_forbidden:
                    return HTTP.build_response(403, 'Forbidden', headers, 'Forbidden')
                if relative_path is None:
                    return HTTP.build_response(404, 'Not Found', headers, 'File Not Found')
            # print(file_path)
            # print(relative_path)

            if request.method == 'GET':
                if file_path.is_dir():
                    files_and_dirs = list(file_path.iterdir())
                    formatted_list = [{"path": '/' + str(relative_path) + '/' + f.name, "name": f.name} for f in files_and_dirs]
                    if not is_root:
                        formatted_list.append({"path": '/' + str(relative_path), "name": '.'})
                        formatted_list.append({"path": '/' + str(relative_path.parent), "name": '..'})
                    out = self.render.make_main_page('/' + str(relative_path), formatted_list)
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
                post_type = request.header.fields.get('')
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
