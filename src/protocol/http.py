class http_header:
    def __init__(self, raw_header=None) -> None:
        self.fields = {} if raw_header is None else self.parse_header(raw_header)

    def parse_header(self, raw_header):
        headers = {}
        lines = raw_header.split("\r\n")
        for line in lines:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value
        return headers

    def to_raw_data(self):
        return (
            "\r\n".join(f"{key}: {value}" for key, value in self.fields.items())
            + "\r\n\r\n"
        )


class http_packet:
    def __init__(self, raw_data=None, header=None, body=None) -> None:
        self.header = header if header is not None else http_header()
        self.body = body
        self.raw_data = raw_data
        if raw_data:
            self.parse_raw_data(raw_data)

    def parse_raw_data(self, raw_data):
        # Split the raw data into header and body
        parts = raw_data.split("\r\n\r\n", 1)
        if len(parts) == 2:
            self.header = http_header(parts[0])
            self.body = parts[1]

    def to_raw_data(self):
        # Convert the packet back to raw data
        header_raw_data = self.header.to_raw_data()
        return header_raw_data + self.body if self.body else header_raw_data


def parse_http(data) -> http_packet:
    return http_packet(raw_data=data)


def build_response(status_code, status_text, headers, body):
    header = http_header()
    header.fields["HTTP/1.1"] = f"{status_code} {status_text}"
    for key, value in headers.items():
        header.fields[key] = value
    return http_packet(header=header, body=body)
