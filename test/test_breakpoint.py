import pathlib
import requests


def test_breakpoint():
    addr = "127.0.0.1"
    port = 11451
    print(pathlib.Path(__file__).parent.resolve())
    url = f"http://{addr}:{port}/123/a.txt"
    data = {}
    headers = {"Authorization": "Basic MTIzOjEyMw==", "Range": "0-1,1-2,2-3"}
    r = requests.get(url=url, data=data, headers=headers)
    res = r.content.decode()
    expect_res = r"""--THISISMYSELFDIFINEDBOUNDARY
Content-Type: text/plain
Content-Range: bytes 0-1/11

sa
--THISISMYSELFDIFINEDBOUNDARY
Content-Type: text/plain
Content-Range: bytes 1-2/11

ad
--THISISMYSELFDIFINEDBOUNDARY
Content-Type: text/plain
Content-Range: bytes 2-3/11

df
--THISISMYSELFDIFINEDBOUNDARY--"""
    assert res == expect_res.replace("\n", "\r\n")
