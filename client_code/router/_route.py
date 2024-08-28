import anvil.server

from ._constants import NETWORK_FIRST
from ._exceptions import NotFound, Redirect
from ._meta import default_description, default_title
from ._navigate import nav_args_to_location, navigate
from ._segments import Segment
from ._utils import encode_query_params, trim_path

sorted_routes = []


def _create_server_route(cls):
    # local for now while anvil uplink doesn't have history
    from anvil.history import Location

    from ._loader import CachedData
    from ._matcher import get_match

    path = cls.path

    if path is None:
        return

    @anvil.server.route(path)
    def route_handler(*args, **kwargs):
        request = anvil.server.request
        path = request.path
        search = encode_query_params(request.query_params)
        location = Location(path=path, search=search, key="default")
        match = get_match(location=location)
        if match is None:
            raise Exception("No match")

        route = match.route
        query = match.query
        params = match.params
        deps = match.deps

        cache = {}

        try:
            route.before_load(path=path, query=query, params=params, hash=match.hash)
        except Redirect as r:
            location = nav_args_to_location(
                path=r.path,
                query=r.query,
                params=r.params,
                hash=r.hash,
            )
            url = (
                anvil.server.get_app_origin()
                + location.path
                + location.search
                + location.hash
            )
            return anvil.server.HttpResponse(status=302, headers={"Location": url})
        except (NotFound, Exception):
            # TODO: handle error on the client
            return anvil.server.LoadAppResponse(data={"cache": cache})

        try:
            data = route.loader(
                location=location,
                params=params,
                query=query,
                deps=deps,
            )

        except (NotFound, Exception):
            # TODO: handle error on the client
            return anvil.server.LoadAppResponse(data={"cache": cache})

        cached_data = CachedData(data=data, location=location, mode=route.cache_mode)
        cache = {match.key: cached_data}

        return anvil.server.LoadAppResponse(data={"cache": cache})


class Route:
    path = None
    segments = []
    form = None
    stale_time = 0
    pending_form = None
    pending_min = 0.5
    pending_delay = 1
    cache_mode = NETWORK_FIRST
    cache_form = False
    error_form = None
    not_found_form = None
    server_fn = None
    server_silent = False

    @classmethod
    def create(cls, *, path=None, form=None, server_fn=None, **props):
        name = f"{form or 'CreatedRoute'}Route"
        cls_dict = {"path": path, "form": form, "server_fn": server_fn}
        for key, value in props.items():
            if callable(value):
                cls_dict[key] = staticmethod(value)
            else:
                cls_dict[key] = value

        return type(name, (cls,), cls_dict)

    def before_load(self, **loader_args):
        pass

    def loader_deps(self, **loader_args):
        return {}

    def loader(self, **loader_args):
        return None

    def meta(self, **loader_args):
        return {"title": default_title, "description": default_description}

    def parse_params(self, params):
        return params

    # def params(self, params):
    #     return params

    def parse_query(self, query):
        return query

    # def prepare_query(self, query):
    #     return query

    def __init_subclass__(cls) -> None:
        if cls.path is not None:
            if not isinstance(cls.path, str):
                raise TypeError("path must be a string")

            trimmed_path = trim_path(cls.path)
            cls.segments = Segment.from_path(trimmed_path)
            if trimmed_path.startswith("."):
                raise ValueError("Route path cannot be relative")

            if not trimmed_path.startswith("/"):
                cls.path = "/" + trimmed_path
            else:
                cls.path = trimmed_path

            sorted_routes.append(cls())

        server_fn = cls.__dict__.get("server_fn")
        existing_loader = cls.__dict__.get("loader")
        if server_fn is not None and existing_loader is None:

            def loader(self, **loader_args):
                if self.server_silent:
                    return anvil.server.call_s(server_fn, **loader_args)
                else:
                    return anvil.server.call(server_fn, **loader_args)

            cls.loader = loader

        if anvil.is_server_side():
            _create_server_route(cls)


def open_form(form, **form_properties):
    if anvil.is_server_side():
        raise RuntimeError("open_form is not available on the server")

    if not isinstance(form, str):
        raise TypeError("form must be a string")

    for route in sorted_routes:
        if route.form != form:
            continue

        if any(segment.is_param() for segment in route.segments):
            raise ValueError(
                f"Tried to call open_form with {form} but {route.path} requires path params"
            )

        return navigate(path=route.path, form_properties=form_properties)

    raise ValueError(f"No route found for form {form}")
