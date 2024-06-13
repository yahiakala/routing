import anvil
from .routes import sorted_routes
from .matcher import get_matches
from .loader import load_data, cache


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
        data = load_data(match)
        form = match.route.form
        print(form)
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

        print("STARTUP DATA")
        if startup_data is not None:
            cache = startup_data.get("cache", {})
            for key, val in cache.items():
                print(key, val.__dict__)
        history.listen(listener)
        navigate()
        # TODO navigate to the first page
