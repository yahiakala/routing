class Route:
    pass


class HomeRoute(Route):
    path = "/"

    @staticmethod
    def __loader__():
        pass

    @classmethod
    def render():
        pass

class ArticleRoute(Route):
    path = "/articles"

    def render(afe):
        pass
