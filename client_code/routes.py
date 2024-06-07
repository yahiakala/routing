import anvil.server

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
