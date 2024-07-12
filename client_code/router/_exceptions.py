from anvil.server import AnvilWrappedError, _register_exception_type


class Redirect(AnvilWrappedError):
    def __init__(self, *, path=None, search_params=None, path_params=None, hash=""):
        self.path = path
        self.search_params = search_params
        self.path_params = path_params
        self.hash = hash


class NotFound(AnvilWrappedError):
    pass


class InvalidPathParams(Exception):
    pass


_register_exception_type(f"{Redirect.__module__}.Redirect", Redirect)
_register_exception_type(f"{NotFound.__module__}.NotFound", NotFound)
