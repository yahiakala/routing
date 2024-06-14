try:
    from anvil.http import url_decode as unquote
except ImportError:
    from urllib.parse import unquote


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

def timeout(ms=0):
    from anvil.js.window import Promise, setTimeout
    def wait_async(resolve, reject):
        def timeout():
            resolve(TIMEOUT)
        setTimeout(timeout, ms)

    return Promise(wait_async)
