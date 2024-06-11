import json

from .utils import trim_path
from .routes import sorted_routes

try:
    from anvil.http import url_decode
except ImportError:
    from urllib.parse import unquote
    def url_decode(s):
        return unquote(s)


class Match:
    def __init__(self, location) -> None:
        self.location = location
        self.path_params = {}
        self.search_params = {}
        self.route = None


def get_segments(path):
    return path.split("/")

def get_matches(location):
    path = trim_path(location.path)
    parts = path.split("/")

    for route in sorted_routes:
        print(route, route.segments)

        iter_segments = iter(route.segments)
        match = Match(location)

        if len(parts) != len(route.segments):
            # todo splat
            continue

        for part in parts:
            try:
                segment = next(iter_segments)
                if segment.type == "static":
                    if part != segment.value:
                        break
                elif segment.type == "param":
                    match.path_params[segment.value] = url_decode(part)
                else:
                    raise Exception("Unknown segment type")
            except StopIteration:
                break
        
        else: # if no break
            match.route = route
            match.search_params = parse_search(match)
            match.path_params = parse_path(match)
            return match

    return None

def parse_search(match):
    search_params = match.location.search_params

    for key, value in dict(search_params).items():
        try:
            search_params[key] = json.loads(value)
        except Exception:
            search_params[key] = value

    parser = match.route.parse_search_params
    if callable(parser):
        return parser(search_params)
    elif hasattr(parser, "parse"):
        return parser.parse(search_params)
    else:
        return search_params


def parse_path(match):
    parser = match.route.parse_path_params
    if callable(parser):
        return parser(match.path_params)
    elif hasattr(parser, "parse"):
        return parser.parse(match.path_params)
    else:
        return match.path_params

