import anvil
from .constants import TIMEOUT

try:
    from anvil.http import url_decode as unquote
except ImportError:
    from urllib.parse import unquote

if anvil.is_server_side():
    from .utils_server import Promise, await_promise, report_exceptions, timeout
else:
    from .utils_client import Promise, await_promise, report_exceptions, timeout


def url_decode(s):
    return unquote(s)


def trim_path(path):
    start = 0
    end = len(path)
    while start < end and path[start] == "/":
        start += 1
    while end > start and path[end - 1] == "/":
        end -= 1
    return path[start:end]


TIMEOUT = object()


