from ._navigate import nav_args_to_location


def get_url(*, path, path_params=None, search_params=None, hash=None):
    location = nav_args_to_location(
        path=path, path_params=path_params, search_params=search_params, hash=hash
    )
    return location.get_url(True)
