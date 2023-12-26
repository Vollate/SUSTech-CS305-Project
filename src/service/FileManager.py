import base64
import json
import shutil
from pathlib import Path
from src.utils import HTML
from src.protocol import HTTP


def find_relative_path_to_target_folder(path, target_folder_name):
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


def remove_boundary(data, boundary):
    tmp = data.split(b'\r\n--' + boundary.encode() + b'--\r\n')
    res = tmp[0]
    for i in range(1, len(tmp)):
        res += tmp[i]
    return res


def get_boundary(request):
    boundary = request.header.fields.get('Content-Type').split('boundary=')[1]
    return boundary


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

    def process(self, data, status: HTTP.HTTPStatus):
        headers = {}
        request = HTTP.HTTP_Request()
        if status.receive_partially:
            # print("partially receive data")
            status.current_receive_size += len(data)
            status.receive_buffer += data
            # print(
            #     f"receive partially: {status.current_receive_size}/{status.expect_receive_size}, length of file {len(status.receive_buffer)}")
            if status.current_receive_size < status.expect_receive_size:
                return None
            elif status.current_receive_size == status.expect_receive_size:
                request = status.request
                request.body_without_boundary = remove_boundary(status.receive_buffer, status.boundary)
                status.receive_partially = False
                pass
            else:
                print("receive too much data, discard")
                request.body = status.receive_buffer
                status.receive_partially = False
                return None
        else:
            # print("current not receive partially")
            request = HTTP.parse_request(data)
            length = request.header.fields.get('Content-Length')
            if length and request.body and int(length) > len(request.body):
                status.receive_partially = True
                status.request = request
                status.current_receive_size = len(request.body)
                status.expect_receive_size = int(length)
                status.receive_buffer = request.body_without_boundary
                status.boundary = get_boundary(request)
                return None

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

            if request.method == 'GET':
                
                LIST_MODE = False
                if(request.url.find('?') != -1):
                    relative_path, query = request.url.split('?', 1)
                    relative_path = Path(relative_path)
                    query, id = query.split('=', 1)
                    if query == 'SUSTech-HTTP' and id == '1':
                        LIST_MODE = True
                    elif query == 'SUSTech-HTTP' and id == '0':
                        LIST_MODE = False
                    else :
                        return HTTP.build_response(400, 'Bad Request', headers, 'Bad Request')     
                    is_root = relative_path.name == '' or relative_path.name == username[0]
                else:
                    is_root = request.url == '' or request.url == username[0]
                    relative_path = Path(request.url)
                
                if not (dir_path / username[0]).exists():
                    (dir_path / username[0]).mkdir()

                if is_root:
                    file_path = dir_path / username[0]
                    relative_path = Path(username[0])
                else:
                    file_path = dir_path / relative_path
                    is_forbidden, relative_path = find_relative_path_to_target_folder(file_path, username[0])
                    if is_forbidden:
                        return HTTP.build_response(403, 'Forbidden', headers, 'Forbidden')
                    if relative_path is None:
                        return HTTP.build_response(404, 'Not Found', headers, 'File Not Found')
                # print(file_path)
                # print(relative_path)
                if file_path.is_dir():
                    files_and_dirs = list(file_path.iterdir())
                    
                    # SUSTech-HTTP
                    if LIST_MODE:
                        formatted_list = [f.name + '/' if f.is_dir() else f.name for f in files_and_dirs]
                        headers['Content-Type'] = 'text/html'
                        headers['Content-Length'] = len(str(formatted_list))
                        return HTTP.build_response(200, 'OK', headers) ,str(formatted_list).encode()
                    else:
                        formatted_list = []
                        if not is_root:
                            formatted_list.append({"path": '/' + str(relative_path)+'/', "name": './'})
                            formatted_list.append({"path": '/' + str(relative_path.parent)+'/', "name": '../'})
                        formatted_list += [{"path": '/' + str(relative_path) + '/' + f.name + '/', "name": f.name+'/'} if f.is_dir() else {"path": '/' + str(relative_path) + '/' + f.name, "name": f.name} for f in files_and_dirs]
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
                method, relative_path = request.url.split('?', 1)
                path_flag, relative_path = relative_path.split('=', 1)
                if path_flag != 'path':
                    return HTTP.build_response(400, 'Bad Request', headers, 'Bad Request')
                relative_path = Path(relative_path)

                file_path = Path(str(dir_path) + str(relative_path))

                is_forbidden, _ = find_relative_path_to_target_folder(file_path, username[0])
                if is_forbidden:
                    return HTTP.build_response(403, 'Forbidden', headers, 'Forbidden')

                if method == 'upload':
                    if not request.body:
                        return HTTP.build_response(400, 'Bad Request', headers, 'No Data to Save')
                    if file_path.is_dir():
                        return HTTP.build_response(400, 'Bad Request', headers, 'Invalid File Path')
                    with file_path.open('wb') as file:
                        file.write(request.body_without_boundary)
                    return HTTP.build_response(200, 'OK', headers, 'File Saved')

                elif method == 'delete':
                    if not file_path.exists():
                        return HTTP.build_response(404, 'Not Found', headers, 'File Not Found')
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                    file_path = file_path.parent
                    relative_path = relative_path.parent
                    files_and_dirs = list(file_path.iterdir())
                    formatted_list = []
                    if not (file_path.name == username[0]):
                        formatted_list.append({"path": str(relative_path), "name": '.'})
                        formatted_list.append({"path": str(relative_path.parent), "name": '..'})
                    formatted_list += [{"path": str(relative_path.parent) + '/' + f.name, "name": f.name} for f in
                                       files_and_dirs]
                    out = self.render.make_main_page(str(relative_path), formatted_list)
                    headers['Content-Type'] = 'text/html'
                    headers['Content-Length'] = str(len(out))
                    return HTTP.build_response(200, 'OK', headers, out)
                else:
                    return HTTP.build_response(400, 'Bad Request', headers, 'Bad Request')

            else:
                return HTTP.build_response(405, 'Method Not Allowed', headers, 'Method Not Allowed')

        except Exception as e:
            return HTTP.build_response(500, 'Internal Server Error', headers, str(e))
