# ruff:noqa: F401
import json

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


def valid_absolute_path(path):
    if not isinstance(path, str):
        raise TypeError("path must be a string")
    trimmed_path = trim_path(path)
    if trimmed_path.startswith("."):
        raise ValueError("Route path cannot be relative")
    return "/" + trimmed_path


def ensure_dict(value, name):
    if value is None:
        return {}
    elif not isinstance(value, dict):
        raise TypeError(f"{name} must be a dict")
    return value


def make_key(path, deps):
    deps = ensure_dict(deps, "deps")
    try:
        json_deps = json.dumps(deps, sort_keys=True)
    except Exception:
        raise TypeError("loader_deps must return a json serializable dict")

    return f"{path}:{json_deps}"


def decode_key(key):
    parts = key.split(":", 1)
    path, deps = parts
    return path, json.loads(deps)