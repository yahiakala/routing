# ruff:noqa: F401
import anvil

from .._constants import TIMEOUT

if anvil.is_server_side():
    from .server import (
        Promise,
        await_promise,
        document,
        encode_query_params,
        report_exceptions,
        setTimeout,
        timeout,
        url_decode,
        url_encode,
    )

    # TODO: remove this at some point
    anvil.server.call_s = anvil.server.call

    class LoadingIndicator:
        def __enter__(self):
            pass

        def __exit__(self, *args):
            pass

    anvil.server.no_loading_indicator = LoadingIndicator()

else:
    from .client import (
        Promise,
        await_promise,
        document,
        encode_query_params,
        report_exceptions,
        setTimeout,
        timeout,
        url_decode,
        url_encode,
    )


def trim_path(path):
    start = 0
    end = len(path)
    while start < end and path[start] == "/":
        start += 1
    while end > start and path[end - 1] == "/":
        end -= 1
    return path[start:end]


def ensure_dict(value, name):
    if value is None:
        return {}
    elif not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")
    return value
