class Route:
    pass


class HomeRoute(Route):
    path = "/"

    @staticmethod
    def __loader__():
        pass

    @staticmethod
    def render():
        pass

class ArticleRoute(Route):
    path = "/articles"

    def render(se):
        pass
        