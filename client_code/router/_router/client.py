from time import sleep

import anvil
from anvil.history import history
from anvil.js import window
from anvil.js.window import WeakMap

from .. import _navigate
from .._cached import CACHED_FORMS
from .._context import RoutingContext
from .._exceptions import NotFound, Redirect
from .._loader import CACHED_DATA, load_data_promise
from .._logger import logger
from .._matcher import get_match
from .._meta import update_meta_tags
from .._navigate import navigate
from .._utils import TIMEOUT, Promise, await_promise, ensure_dict, timeout
from .._view_transition import ViewTransition

waiting = False
undoing = False
redirect = True
current = {"delta": None}

navigation_blockers = set()
before_unload_blockers = set()

form_to_context = WeakMap()


def get_context(form) -> RoutingContext:
    rv = form_to_context.get(form)
    if rv is None:
        raise ValueError(f"No context for form {form}")
    return rv


class _NavigationEmitter:
    def __init__(self):
        self._subscribers = set()

    def subscribe(self, fn):
        self._subscribers.add(fn)

    def unsubscribe(self, fn):
        self._subscribers.discard(fn)

    def emit(self, event_name, **kwargs):
        kwargs["event_name"] = event_name
        for fn in self._subscribers:
            fn(**kwargs)


navigation_emitter = _NavigationEmitter()


def _beforeunload(e):
    e.preventDefault()  # cancel the event
    e.returnValue = ""  # chrome requires a returnValue to be set


class UnloadBlocker:
    def block(self):
        if not before_unload_blockers:
            window.addEventListener("beforeunload", _beforeunload)
        before_unload_blockers.add(self)

    def unblock(self):
        before_unload_blockers.remove(self)
        if not before_unload_blockers:
            window.removeEventListener("beforeunload", _beforeunload)


class NavigationBlocker:
    def __init__(self, warn_before_unload=False):
        self.warn_before_unload = warn_before_unload
        self.unload_blocker = UnloadBlocker()

    def __enter__(self):
        self.block()
        return self

    def __exit__(self, *args):
        self.unblock()
        return False

    def block(self):
        global waiting
        waiting = True
        navigation_blockers.add(self)
        if self.warn_before_unload:
            self.unload_blocker.block()

    def unblock(self):
        global waiting
        navigation_blockers.remove(self)
        waiting = bool(navigation_blockers)
        if self.warn_before_unload:
            self.unload_blocker.unblock()


def stop_unload():
    global undoing
    undoing = True
    delta = current.get("delta")
    if delta is not None:
        history.go(-delta)
    sleep(0)  # give control back to event loop


def on_navigate():
    location = history.location
    logger.debug("navigating")
    key = location.key
    nav_context = _navigate._current_nav_context
    form_properties = _navigate._current_form_properties

    def is_stale():
        stale = key != history.location.key
        if stale:
            logger.debug(f"stale navigation detected exiting: {location}")
        return stale

    prev_context = RoutingContext._current
    if prev_context is not None:
        with NavigationBlocker():
            if prev_context._prevent_unload():
                logger.debug(f"navigation blocked by {prev_context.location}")
                stop_unload()
                return

    match = get_match(location)
    if match is None:
        raise Exception(f"No match {location}")

    context = RoutingContext(
        match=match, nav_context=nav_context, form_properties=form_properties
    )

    route = match.route

    pending_form = route.pending_form
    pending_delay = route.pending_delay
    pending_min = route.pending_min

    def handle_error(form_attr, error):
        if is_stale():
            return
        logger.debug(f"navigation error: {error}")
        context.set_data(None, error)

        form = getattr(route, form_attr, None)
        if form is None:
            raise error

        with ViewTransition():
            anvil.open_form(form, routing_context=context)

    try:
        route.before_load(**context._loader_args)
    except Redirect as r:
        return navigate(**r.__dict__, replace=True)
    except NotFound as e:
        return handle_error("not_found_form", e)
    except Exception as e:
        return handle_error("error_form", e)

    # Optimistically update meta tags before opening the form
    meta = route.meta(**context._loader_args)
    ensure_dict(meta, "meta")
    update_meta_tags(meta)

    RoutingContext._current = context

    # TODO: how does cached forms work with cache modes for data?
    if match.key in CACHED_FORMS:
        form = CACHED_FORMS[match.key]
        cached_context = get_context(form)
        cached_context._update(context)
        RoutingContext._current = cached_context
        logger.debug(f"cached form is already open: {form}")
        if anvil.get_open_form() is form:
            return
        # TODO: update the context probably
        logger.debug(f"found a cached form for this location: {form}")
        anvil.open_form(form)
        return

    logger.debug(f"Match key {match.key}")
    if prev_context is not None and match.key == prev_context.match.key:
        form = anvil.get_open_form()
        if form is not None and form_to_context.get(form) is prev_context:
            prev_context._update(context)
            logger.debug(f"navigation would return the same form: {form}")
            return

    data_promise = load_data_promise(context)

    try:
        result = Promise.race([data_promise, timeout(pending_delay)])
    except NotFound as e:
        return handle_error("not_found_form", e)
    except Exception as e:
        return handle_error("error_form", e)

    if is_stale():
        return

    if pending_form is not None and result is TIMEOUT:
        logger.debug(
            f"exceeded pending delay: {pending_delay}, loading pending form {pending_form!r}"
        )
        with ViewTransition():
            anvil.open_form(pending_form)
        sleep(pending_min)

    try:
        _, error = await_promise(data_promise)
        if error is not None:
            raise error
    except NotFound as e:
        return handle_error("not_found_form", e)
    except Exception as e:
        return handle_error("error_form", e)

    if is_stale():
        return

    form = route.form
    try:
        with ViewTransition():
            rv = anvil.open_form(
                form, routing_context=context, **context.form_properties
            )
        form_to_context.set(rv, context)
        if route.cache_form:
            CACHED_FORMS[match.key] = rv

    except Exception as e:
        return handle_error("error_form", e)
    # TODO: decide how to cache the form


def listener(**listener_args):
    global waiting, undoing, redirect, current

    if undoing:
        undoing = False
    elif waiting:
        delta = listener_args.get("delta")
        if delta is not None:
            undoing = True
            history.go(-delta)
        else:
            # user determined to navigate
            history.reload()
    else:
        current = listener_args

        if redirect:
            on_navigate()
        else:
            redirect = True

    navigation_emitter.emit("navigate", **listener_args)


def launch():
    from anvil.history import history
    from anvil.server import startup_data

    if startup_data is not None:
        startup_cache = startup_data.get("cache", {})
        CACHED_DATA.update(startup_cache)
        logger.debug(f"startup data: {repr(startup_cache)[:100]}...")

    history.listen(listener)
    on_navigate()
    # TODO navigate to the first page
