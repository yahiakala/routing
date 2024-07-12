from anvil.server import AnvilWrappedError, _register_exception_type

from ._utils import ensure_dict


class Redirect(AnvilWrappedError):
    def __init__(
        self,
        *,
        path=None,
        search_params=None,
        path_params=None,
        hash="",
        nav_args=None,
        form_properties=None,
    ):
        self.path = path
        self.search_params = search_params
        self.path_params = path_params
        self.hash = hash
        self.nav_args = ensure_dict(nav_args, "nav_args")
        self.form_properties = ensure_dict(form_properties, "form_properties")


class NotFound(AnvilWrappedError):
    pass


class InvalidPathParams(Exception):
    pass


_register_exception_type(f"{Redirect.__module__}.Redirect", Redirect)
_register_exception_type(f"{NotFound.__module__}.NotFound", NotFound)
