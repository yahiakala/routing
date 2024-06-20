import re
from time import sleep
import anvil
from .navigate import navigate
from .redirect import Redirect
from .context import Context
from .utils import TIMEOUT, await_promise, timeout, Promise, encode_search_params
from .routes import sorted_routes
from .matcher import get_match
from .loader import load_data, cache, load_data_promise, CachedData


if anvil.is_server_side():

    from urllib.parse import urlencode
    from anvil.history import Location

    def create():

        for route in sorted_routes:

            @anvil.server.route(route.path)
            def route_handler(*args, **kwargs):
                request = anvil.server.request
                path = request.path
                search = encode_search_params(request.query_params)
                location = Location(path=path, search=search, key="default")
                match = get_match(location=location)
                if match is None:
                    raise Exception("No match")

                search_params = match.search_params
                path_params = match.path_params
                deps = match.deps

                data = route.loader(
                    location=location,
                    search_params=search_params,
                    path_params=path_params,
                    deps=deps,
                )

                cached_data = CachedData(data=data, location=location)

                return anvil.server.LoadAppResponse(
                    data={"cache": {match.key: cached_data}}
                )

else:

    from anvil.history import history

    def on_navigate():

        location = history.location
        key = location.key

        def is_stale():
            return key != history.location.key

        match = get_match(location)
        if match is None:
            raise Exception("No match")

        route = match.route
        pending_form = route.pending_form
        pending_delay = route.pending_delay

        try:
            route.before_load()
        except Redirect as r:
            return navigate(**r.__dict__, replace=True)

        prev_context = Context._current
        context = Context._current = Context(match)
        # TODO: decide what to do if only search params change or only hash changes
        # if only search params change, we need to load data
        # but the form might be using navigate_on_search_change=False
        # so we need to emit the search_changed event
        # if hash changes, just emit the hash_changed event

        data_promise = load_data_promise(match)
        result = Promise.race([data_promise, timeout(pending_delay)])

        if is_stale():
            return

        if pending_form is not None and result is TIMEOUT:
            anvil.open_form(pending_form)
            sleep(pending_delay)

        data = await_promise(data_promise)
        if is_stale():
            return

        context.data = data

        form = route.form
        anvil.open_form(form, context=context)

    def listener(args):
        on_navigate()
        # TODO:
        # call get_match
        # if match:
        #   call the loader
        #   load the form with the data
        #   need to ensure that the correct form is open
        # loader needs to be clever!

        pass

    def create():
        from anvil.history import history
        from anvil.server import startup_data

        if startup_data is not None:
            startup_cache = startup_data.get("cache", {})
            cache.update(startup_cache)

        print("STARTUP DATA")
        if startup_data is not None:
            startup_cache = startup_data.get("cache", {})
            for key, val in startup_cache.items():
                print(key, repr(val.__dict__)[:20])

        history.listen(listener)
        on_navigate()
        # TODO navigate to the first page
