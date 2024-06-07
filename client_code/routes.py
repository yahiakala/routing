import anvil.server

from anvil.js.window import WeakMap

formCache = WeakMap()

class CachedRoute:
    def __init__(self, *, location, route, data=None):
        self.location = location
        # and the rest


class Router_:
    def get_cached_route(self, form):
        cached_route = None
        while form.parent is not None:
            cached_route = formCache.get(form)
            if cached_route:
                break    
            form = form.parent

        else: # if no break
            raise Exception("No cached route - you may need to wait for the show event")

        return cached_route

    def get_path_params(self, form):
        return self.get_cached_route(form).path_params

    def get_search_params(self, form):
        return self.get_cached_route(form).search_params

    def get_location(self, form):
        return self.get_cached_route(form).location

    def get_data(self, form):
        return self.get_cached_route(form).data

Router = Router_()


class Route:
    data = None


class HomeRoute(Route):
    path = "/"
    form = "HomeForm"

    def before_load(self):
        pass

    @property
    def form(self):
        from .HomeForm import HomeForm
        return HomeForm

    @property
    def error_form(self):
        pass

    def loader(self):
        pass

    def validate_search(self):
        pass

    def parse_params(self):
        pass

    def dump_params(self):
        pass



class ArticlesRoute(Route):
    path = "/articles"
    form = "ArticlesForm"

    @staticmethod
    def loader():
        # could use context here - we need to be paricularly careful about open form
        # because open form can be asyncronous in some ways
        # i.e. multiple open forms can be called in flight
        # so if we use context - we'll want to do our clever __new__ thing
        # attach the context (maybe through a weak map)
        # then call the API with self
        # e.g. routing.get_data(self) - probably
        # caching will be fun here
        # search params, path params
        return anvil.server.call("load_articles")

