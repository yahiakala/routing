from .constants import TIMEOUT

from anvil.js.window import Promise, setTimeout, URLSearchParams
from anvil.js import await_promise
from anvil.js import report_exceptions

def timeout(ms=0):
    def wait_async(resolve, reject):
        def timeout():
            resolve(TIMEOUT)

        setTimeout(timeout, ms)

    return Promise(wait_async)

def encode_search_params(search_params):
    if not search_params:
        return ""

    return "?" + URLSearchParams(search_params).toString()
