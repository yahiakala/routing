import json

from anvil.history import Location, history

from ._constants import NOT_FOUND
from ._exceptions import InvalidPathParams
from ._logger import logger
from ._segments import Segment
from ._utils import encode_query_params, ensure_dict, url_encode


def clean_path(path, params):
    if path is None:
        return history.location.path

    # remove leading dots
    segments = Segment.from_path(path)

    leading_dots = path.startswith(".")

    path = ""

    for segment in segments:
        if segment.is_static():
            path += "/" + url_encode(segment.value)
        elif segment.is_param():
            value = params.get(segment.value, NOT_FOUND)
            if value is NOT_FOUND:
                raise InvalidPathParams(f"No path param for {segment.value}")
            path += "/" + url_encode(str(value))

    if leading_dots:
        path = path[1:]

    return path


def stringify_value(val):
    if not isinstance(val, str):
        return json.dumps(val, sort_keys=True)

    try:
        # this way strings are flat like foo=bar
        # and already jsonified strings are returned as is
        val = json.loads(val)
        return json.dumps(val)
    except Exception:
        return val


def clean_query_params(query):
    if not query:
        return {}

    real_query = {}
    keys = sorted(query.keys())
    for key in keys:
        real_query[key] = stringify_value(query[key])

    return real_query


def nav_args_to_location(*, path, query, params, hash):
    params = params or {}
    query = clean_query_params(query)
    search = encode_query_params(query)
    path = clean_path(path, params)

    return Location(path=path, search=search, hash=hash)


_current_nav_args = {}
_current_form_properties = {}


def navigate_with_location(
    location, replace=False, nav_args=None, form_properties=None
):
    global _current_nav_args, _current_form_properties

    nav_args = ensure_dict(nav_args, "nav_args")
    form_properties = ensure_dict(form_properties, "form_properties")

    _current_nav_args = nav_args
    _current_form_properties = form_properties
    current_location = history.location

    if (
        current_location.path == location.path
        and current_location.search == location.search
        and current_location.hash == location.hash
    ):
        logger.debug("unchanged navigation location - exiting")
        return

    if replace:
        history.replace(location)
    else:
        history.push(location)


def navigate(
    location_or_url_or_path=None,
    *,
    path=None,
    params=None,
    query=None,
    hash="",
    replace=False,
    nav_args=None,
    form_properties=None,
):
    logger.debug(
        f"navigate called with: {location_or_url_or_path!r} "
        f"path={path!r} "
        f"params={params!r} "
        f"query={query!r} "
        f"hash={hash!r} "
        f"replace={replace!r} "
        f"nav_args={nav_args!r} "
        f"form_properties={form_properties!r}"
    )
    if location_or_url_or_path is not None:
        if isinstance(location_or_url_or_path, Location):
            temp_location = location_or_url_or_path
        elif isinstance(location_or_url_or_path, str):
            temp_location = Location.from_url(location_or_url_or_path)
        else:
            raise TypeError("location_or_url_or_path must be a string or a Location")

        if path is not None:
            raise TypeError("cannot set named argument path if a first argument is set")

        location = nav_args_to_location(
            path=temp_location.path,
            query=query,
            params=params,
            hash=hash or temp_location.hash,
        )

        # search params on a raw location are a bit gnarly
        # they are json stringified so we would be json stringifying again - let's not do that
        if not location.search and temp_location.search:
            location.search = temp_location.search

    else:
        location = nav_args_to_location(
            path=path, query=query, params=params, hash=hash
        )
    logger.debug(f"navigate location: {location}")

    nav_args = ensure_dict(nav_args, "nav_args")
    form_properties = ensure_dict(form_properties, "form_properties")

    return navigate_with_location(
        location, replace=replace, nav_args=nav_args, form_properties=form_properties
    )
