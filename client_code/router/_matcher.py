import json

from ._navigate import get_nav_location
from ._route import Route, sorted_routes
from ._utils import make_key, trim_path, url_decode, loads


class Match:
    def __init__(self, location, params, query, route: Route) -> None:
        self.location = location
        self.path = location.path
        self.params = params
        self.hash = location.hash
        self.query = query
        self.route = route
        self.deps = route.cache_deps(
            path=self.path, params=params, query=query, hash=self.hash
        )
        self.key = make_key(self.path, self.deps)


def get_segments(path):
    return path.split("/")


def get_match_from_nav_args(context_or_path_or_url, *, path, query, params, hash):
    from ._context import RoutingContext

    # fast path
    if path is None and query is None and params is None and hash is None:
        if isinstance(context_or_path_or_url, RoutingContext):
            return context_or_path_or_url.match

    location = get_nav_location(
        context_or_path_or_url, path=path, query=query, params=params, hash=hash
    )
    match = get_match(location)
    if match is None:
        raise Exception(f"No match {location}")
    return match


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


def ensure_dict_wrapper(fn):
    def wrapper(*args, **kws):
        rv = fn(*args, **kws)
        if rv is None:
            return {}
        if not isinstance(rv, dict):
            raise TypeError(f"{fn.__name__} must return a dict")
        return rv

    return wrapper


@ensure_dict_wrapper
def parse_query(route: Route, query: dict):
    for key, value in dict(query).items():
        try:
            query[key] = loads(value)
        except Exception:
            pass

    parser = route.parse_query
    if callable(parser):
        return parser(query)
    elif hasattr(parser, "parse"):
        return parser.parse(query)
    else:
        return query


@ensure_dict_wrapper
def parse_path(route: Route, params: dict):
    for key, value in dict(params).items():
        try:
            params[key] = loads(value)
        except Exception:
            pass

    parser = route.parse_params
    if callable(parser):
        return parser(params)
    elif hasattr(parser, "parse"):
        return parser.parse(params)
    else:
        return params
