# ruff: noqa: F401, F811
from anvil.history import history as _history

from ._cached import clear_cache
from ._constants import (
    CACHE_FIRST,
    LAYOUTS,
    NETWORK_FIRST,
    NO_CACHE,
    STALE_WHILE_REVALIDATE,
    TEMPLATE_WITH_CONTAINER,
)
from ._context import RoutingContext
from ._exceptions import NotFound, Redirect
from ._invalidate import invalidate
from ._logger import debug_logging
from ._navigate import navigate
from ._route import Route, open_form
from ._router import NavigationBlocker, launch, navigation_emitter
from ._url import get_url
from ._view_transition import use_transitions


def subscribe(event_name, fn):
    return navigation_emitter.subscribe(event_name, fn)


def unsubscribe(event_name, fn):
    return navigation_emitter.unsubscribe(event_name, fn)


def go(n=0):
    return _history.go(n)


def back():
    return _history.go(-1)


def forward():
    return _history.go(1)


def get_routing_context():
    return RoutingContext._current


def reload(hard=False):
    if hard:
        return _history.reload()
    else:
        invalidate(path=_history.location.path)
        _history.replace(_history.location)
