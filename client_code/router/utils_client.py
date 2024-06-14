from .constants import TIMEOUT

from anvil.js.window import Promise, setTimeout
from anvil.js import await_promise
from anvil.js import report_exceptions

def timeout(ms=0):
    def wait_async(resolve, reject):
        def timeout():
            resolve(TIMEOUT)

        setTimeout(timeout, ms)

    return Promise(wait_async)
