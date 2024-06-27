from anvil.server import _register_exception_type as _register_exception


class Redirect(Exception):
    def __init__(self, *, path=None, search_params=None, path_params=None, hash=""):
        self.path = path
        self.search_params = search_params
        self.path_params = path_params
        self.hash = hash


class NotFound(Exception):
    pass


_register_exception(f"{Redirect.__module__}.Redirect", Redirect)
_register_exception(f"{NotFound.__module__}.NotFound", NotFound)
