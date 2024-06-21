from ._navigate import nav_args_to_location
from anvil.history import history

def get_url(*, path, path_params, search_params, hash):
    location = nav_args_to_location(path, path_params, search_params, hash)
    history.createHref(location)
