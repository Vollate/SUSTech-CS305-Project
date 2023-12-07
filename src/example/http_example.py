from protocol import http
from utils import html

render = html.html_render("templates", "template.html")
title = "foo"
files = [{"path": "p1", "name": "n1"}, {"path": "p2", "name": "n2"}]
out = render.make_html(title, files)

eg_fields = {}
eg_fields["Content-Type"] = "text/html"
eg_fields["Keep-Alive"] = "timeout=15, max=100"
packet = http.build_response(200, 'OK', eg_fields, out)

print(packet.to_raw_data())

raw_request = "POST /submit-form HTTP/1.1\r\n" \
               "Host: www.example.com\r\n" \
               "Content-Type: application/x-www-form-urlencoded\r\n" \
               "Content-Length: 27\r\n" \
               "\r\n" \
               "field1=value1&field2=value2"

request=http.parse_request(raw_request)
print(request.header.fields)