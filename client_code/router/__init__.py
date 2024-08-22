# ruff: noqa: F401
from anvil.history import history as _history

from ._cached import clear_cache
from ._constants import NETWORK_FIRST, STALE_WHILE_REVALIDATE
from ._context import RoutingContext
from ._exceptions import NotFound, Redirect
from ._logger import debug_logging
from ._navigate import navigate
from ._route import Route, open_form
from ._router import NavigationBlocker, UnloadBlocker, launch
from ._url import get_url


def go(n=0):
    return _history.go(n)


def back():
    return _history.go(-1)


def forward():
    return _history.go(1)


def reload():
    return _history.reload()


def get_routing_context():
    return RoutingContext._current
