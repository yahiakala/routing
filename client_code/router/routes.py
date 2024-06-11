from client_code.router.utils import trim_path


sorted_routes = []

PARAM = "param"
STATIC = "static"


class Segment:
    def __init__(self, type, value):
        self.type = type
        self.value = value


class Route:
    path = ""
    form = None

    def __init__(self):
        path = trim_path(self.path)
        parts = path.split("/")
        segments = []
        for part in parts:
            if part.startswith(":"):
                segments.append(Segment(PARAM, part[1:]))
            else:
                segments.append(Segment(STATIC, part))

        self.segments = segments

    def parse_path_params(self, path_params):
        return path_params

    def parse_search_params(self, search_params):
        return search_params

    def __init_subclass__(cls) -> None:
        # TODO sort the routes by path specificity
        print("adding route", cls)
        sorted_routes.append(cls())
