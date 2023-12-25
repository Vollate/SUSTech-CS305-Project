class http_header:
    def __init__(self, raw_header=None) -> None:
        self.fields = {}
        if raw_header is not None:
            self.fields = self.parse_header(raw_header)

    def parse_header(self, raw_header):
        headers = {}
        lines = raw_header.split("\r\n")
        for line in lines:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value
        return headers

    def to_raw_data(self):
        return "\r\n".join(f"{key}: {value}" for key, value in self.fields.items()) + "\r\n\r\n"


class http_request:
    def __init__(self, raw_data) -> None:
        self.raw_data = raw_data
        self.method = None
        self.url = None
        self.http_version = None
        self.header = http_header()
        self.body = None
        self.parse_raw_data()

    def parse_raw_data(self):
        parts = self.raw_data.split("\r\n\r\n", 1)
        header_body = parts[0].split("\r\n", 1)
        request_line = header_body[0]
        self.method, self.url, self.http_version = request_line.split(' ', 2)
        self.header = http_header(header_body[1])
        if len(parts) == 2:
            self.body = parts[1]


class http_response:
    def __init__(self, status_code, status_text, headers, body=None):
        self.status_code = status_code
        self.status_text = status_text
        self.headers = headers
        self.body = body

    def encode(self):
        return self.to_raw_data().encode()

    def to_raw_data(self):
        header_raw_data = self.headers.to_raw_data()
        if self.body:
            return "HTTP/1.1 {} {}\r\n".format(self.status_code,
                                           self.status_text) + header_raw_data+self.body
        return "HTTP/1.1 {} {}\r\n".format(self.status_code,
                                           self.status_text) + header_raw_data


def parse_request(data) -> http_request:
    return http_request(data)


def build_response(status_code, status_text, headers, body=None):
    header = http_header()
    for key, value in headers.items():
        header.fields[key] = value
    return http_response(status_code, status_text, header, body)


# header
def build_header(header_set):
    header = http_header()
    for key, value in header_set.items():
        header.fields[key] = value
    return header
