import json

from ._route import Route, sorted_routes
from ._utils import trim_path, url_decode


class Match:
    def __init__(self, location, params, query, route: Route) -> None:
        self.location = location
        self.params = params
        self.query = query
        self.route = route
        self.deps = route.loader_deps(location=location, params=params, query=query)
        self.key = f"{self.location.path}:{json.dumps(self.deps, sort_keys=True)}"


def get_segments(path):
    return path.split("/")


def get_match(location):
    path = trim_path(location.path)
    parts = path.split("/")

    for route in sorted_routes:
        iter_segments = iter(route.segments)
        params = {}

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
                    params[segment.value] = url_decode(part)
                else:
                    raise Exception("Unknown segment type")
            except StopIteration:
                break

        else:  # if no break
            params = parse_path(route, params)
            query = parse_query(route, location.search_params)
            return Match(location, params, query, route)

    return None


def parse_query(route: Route, query: dict):
    for key, value in dict(query).items():
        try:
            query[key] = json.loads(value)
        except Exception:
            query[key] = value

    parser = route.parse_query
    if callable(parser):
        return parser(query)
    elif hasattr(parser, "parse"):
        return parser.parse(query)
    else:
        return query


def parse_path(route: Route, params: dict):
    parser = route.parse_params
    if callable(parser):
        return parser(params)
    elif hasattr(parser, "parse"):
        return parser.parse(params)
    else:
        return params
