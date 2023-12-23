import base64
from protocol.http import build_header, build_response, http_request
from service import File_Manager

# Simulate an HTTP request builder
def create_request(method, url, username=None, password=None, body=None):
    headers = build_header({})
    if username and password:
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers.fields['Authorization'] = f"Basic {encoded_credentials}"
    
    if body:
        headers.fields['Content-Type'] = 'text/plain'
        headers.fields['Content-Length'] = str(len(body))

    raw_request = f"{method} {url} HTTP/1.1\r\n{headers.to_raw_data()}"
    if body:
        raw_request += f"\r\n{body}"

    return http_request(raw_request)

# Initialize File_Manager
file_manager = File_Manager()

# Create a test user and password
test_username = 'alice'
test_password = 'senseisuki'  # The password should be the hashed version in the actual `accounts.json`
file_manager.USERS_DB[test_username] = test_password

# Create test requests
authorized_request = create_request('GET', '/testfile', test_username, test_password)
unauthorized_request = create_request('GET', '/testfile', 'wronguser', 'wrongpass')

# Process the test requests
print("Testing with authorized credentials:")
response = file_manager.process(authorized_request.raw_data)
print(response.status_code, response.status_text)
print(response.headers.fields)
print(response.body)

print("\nTesting with unauthorized credentials:")
response = file_manager.process(unauthorized_request.raw_data)
print(response.status_code, response.status_text)
print(response.headers.fields)
print(response.body)
