import json
from re import search

from .utils import trim_path, url_decode
from .routes import Route, sorted_routes


class Match:
    def __init__(self, location, path_params, search_params, route: Route) -> None:
        self.location = location
        self.path_params = path_params
        self.search_params = search_params
        self.route = route

def get_segments(path):
    return path.split("/")


def get_match(location):
    path = trim_path(location.path)
    parts = path.split("/")

    for route in sorted_routes:
        print(route, route.segments)

        iter_segments = iter(route.segments)
        path_params = {}

        if len(parts) != len(route.segments):
            # todo splat
            continue

        for part in parts:
            try:
                segment = next(iter_segments)
                if segment.is_static():
                    if part != segment.value:
                        break
                elif segment.is_param():
                    path_params[segment.value] = url_decode(part)
                else:
                    raise Exception("Unknown segment type")
            except StopIteration:
                break

        else:  # if no break
            path_params = parse_path(route, path_params)
            search_params = parse_search(route, location.search_params)
            return Match(location, path_params, search_params, route)

    return None


def parse_search(route: Route, search_params: dict):
    for key, value in dict(search_params).items():
        try:
            search_params[key] = json.loads(value)
        except Exception:
            search_params[key] = value

    parser = route.parse_search_params
    if callable(parser):
        return parser(search_params)
    elif hasattr(parser, "parse"):
        return parser.parse(search_params)
    else:
        return search_params


def parse_path(route: Route, path_params: dict):
    parser = route.parse_path_params
    if callable(parser):
        return parser(path_params)
    elif hasattr(parser, "parse"):
        return parser.parse(path_params)
    else:
        return path_params
