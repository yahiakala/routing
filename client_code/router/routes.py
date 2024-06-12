from re import S
from .utils import trim_path


sorted_routes = []


class Segment:
    PARAM = "PARAM"
    STATIC = "STATIC"

    def __init__(self, type, value):
        self.type = type
        self.value = value

    @classmethod
    def static(cls, value):
        return cls(cls.STATIC, value)

    @classmethod
    def param(cls, value):
        return cls(cls.PARAM, value)


class Route:
    path = ""
    form = None
    stale_time = 0

    def __init__(self):
        path = trim_path(self.path)
        parts = path.split("/")
        segments = []
        for part in parts:
            if part.startswith(":"):
                segments.append(Segment.param(part[1:]))
            else:
                segments.append(Segment.static(part))

        self.segments = segments

    def loader_deps(self, **loader_args):
        return {}

    def loader(self, **loader_args):
        return None

    def parse_path_params(self, path_params):
        return path_params

    def parse_search_params(self, search_params):
        return search_params

    def __init_subclass__(cls) -> None:
        sorted_routes.append(cls())
