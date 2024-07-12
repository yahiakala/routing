from anvil.designer import in_designer
from anvil.js.window import Promise, URLSearchParams, setTimeout

from .._constants import TIMEOUT

if in_designer:
    pass
else:
    pass


def timeout(s=0):
    def wait_async(resolve, reject):
        def timeout():
            resolve(TIMEOUT)

        setTimeout(timeout, s * 1000)

    return Promise(wait_async)


def encode_search_params(search_params):
    if not search_params:
        return ""

    return "?" + URLSearchParams(search_params).toString()
