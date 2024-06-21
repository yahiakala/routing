from .._constants import TIMEOUT

from anvil.js.window import Promise, setTimeout, URLSearchParams, document
from anvil.js import await_promise
from anvil.js import report_exceptions
from anvil.designer import in_designer

if in_designer:
    from anvil.js.window import encodeURIComponent as url_encode
    from anvil.js.window import decodeURIComponent as url_decode
else:
    from anvil.http import url_encode
    from anvil.http import url_decode


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

