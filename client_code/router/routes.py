from .segments import Segment
from .utils import trim_path


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
