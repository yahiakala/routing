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
        return anvil.server.call("load_articles")

