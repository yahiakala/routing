try:
    from anvil.history import history, Location
except ImportError:
    pass
import json

from ._segments import Segment
from ._utils import trim_path, url_encode, encode_search_params
from ._constants import NOT_FOUND


def clean_path(path, path_params):
    if path is None:
        return None

    segments = Segment.from_path(path)
    path = ""

    for segment in segments:
        if segment.is_static():
            path += "/" + url_encode(segment.value)
        elif segment.is_param():
            value = path_params.get(segment.value, NOT_FOUND)
            if value is NOT_FOUND:
                raise Exception(f"No path param for {segment.value}")
            path += "/" + url_encode(str(value))
    
    return path

def clean_search_params(search_params):
    if not search_params:
        return {}

    real_search_params = {}
    keys = sorted(search_params.keys())
    for key in keys:
        real_search_params[key] = json.dumps(search_params[key], sort_keys=True)


def nav_args_to_location(path, search_params, path_params, hash):
    path_params = path_params or {}
    search_params = clean_search_params(search_params)
    search = encode_search_params(search_params)
    path = clean_path(path, path_params)

    return Location(path=path, search=search, hash=hash)


def navigate(*, path=None, search_params=None, path_params=None, hash="", replace=False):
    location = nav_args_to_location(path, search_params, path_params, hash)
    current_location = history.location
    print("LOCATION", location, current_location)

    if (
        current_location.path == location.path
        and current_location.search == location.search
        and current_location.hash == location.hash
    ):
        print("early exit")
        return

    if replace:
        history.replace(location)
    else:
        history.push(location)
