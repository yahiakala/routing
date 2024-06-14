import anvil
from .constants import TIMEOUT

try:
    from anvil.http import url_decode
    from anvil.http import url_encode
except ImportError:
    from urllib.parse import unquote as url_decode
    from urllib.parse import quote as url_encode

if anvil.is_server_side():
    from .utils_server import Promise, await_promise, report_exceptions, timeout, encode_search_params
else:
    from .utils_client import Promise, await_promise, report_exceptions, timeout, encode_search_params


def trim_path(path):
    start = 0
    end = len(path)
    while start < end and path[start] == "/":
        start += 1
    while end > start and path[end - 1] == "/":
        end -= 1
    return path[start:end]



