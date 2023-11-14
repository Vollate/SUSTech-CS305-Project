
class HTTP_Header:
    def __init__(self) -> None:
        return  # TODO


class HTTP_Packet:
    def __init__(self) -> None:
        self.header = HTTP_Header()
        self.body = None


def parse(data) -> HTTP_Packet:
    return HTTP_Packet()
