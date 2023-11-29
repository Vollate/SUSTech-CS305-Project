import requests
from src.protocol import http


def test_parser():
    res = requests.get("http://example.com")
    print(res)
    #TODO
    pass


def test_builder():
    pass
