from ._navigate import nav_args_to_location


def get_url(*, path, params=None, query=None, hash=None):
    location = nav_args_to_location(path=path, params=params, query=query, hash=hash)
    return location.get_url(True)
