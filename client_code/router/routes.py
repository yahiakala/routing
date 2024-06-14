import anvil.server

from .segments import Segment
from .utils import trim_path, encode_search_params


sorted_routes = []


class Route:
    path = ""
    segments = []
    form = None
    stale_time = 0
    pending_form = None
    pending_min = 0.5
    pending_delay = 1

    def loader_deps(self, **loader_args):
        return {}

    def loader(self, **loader_args):
        return None

    def parse_path_params(self, path_params):
        return path_params

    def parse_search_params(self, search_params):
        return search_params

    def __init_subclass__(cls) -> None:
        cls.path = trim_path(cls.path)
        cls.segments = Segment.from_path(cls.path)
        sorted_routes.append(cls())
        if anvil.is_server_side():
            cls.create_server_route()


    @classmethod
    def create_server_route(cls):
        # local for now while anvil uplink doesn't have history
        from anvil.history import Location
        from .loader import load_data, cache
        from .matcher import get_match

        path = cls.path
        print("registering route", path)

        @anvil.server.route(path)
        def route_handler(*args, **kwargs):
            request = anvil.server.request
            path = request.path
            search = encode_search_params(request.query_params)
            location = Location(path=path, search=search, key="default")
            match = get_match(location=location)
            load_data(match)
            return anvil.server.LoadAppResponse(data={"cache": cache})
