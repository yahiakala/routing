from time import sleep
import anvil
from .utils import TIMEOUT, await_promise, timeout, Promise
from .routes import sorted_routes
from .matcher import get_matches
from .loader import load_data, cache, load_data_promise


if anvil.is_server_side():

    from urllib.parse import urlencode
    from anvil.history import Location

    def create():

        for route in sorted_routes:

            @anvil.server.route(route.path)
            def route_handler(*args, **kwargs):
                request = anvil.server.request
                path = request.path
                query_params = request.query_params
                search = f"?{urlencode(query_params)}" if query_params else ""
                location = Location(path=path, search=search, key="default")
                match = get_matches(location=location)
                load_data(match)
                return anvil.server.LoadAppResponse(data={"cache": cache})

else:

    from anvil.history import history

    def navigate():
        location = history.location
        match = get_matches(location)
        if match is None:
            raise Exception("No match")

        pending_form = match.route.pending_form
        pending_delay = match.route.pending_delay

        data_promise = load_data_promise(match)
        result = Promise.race([data_promise, timeout(pending_delay)])
        print(result)

        if pending_form is not None and result is TIMEOUT:
            anvil.open_form(pending_form)
            sleep(pending_delay)

        data = await_promise(data_promise)
        form = match.route.form
        anvil.open_form(form, data=data)

    def listener(args):
        navigate()
        # TODO:
        # call get_matches
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
        navigate()
        # TODO navigate to the first page
