import pytest
from time import sleep
from urllib.parse import parse_qs, urlparse


from client_code.router.routes import Route, sorted_routes
from client_code.router.matcher import get_matches
from client_code.router.loader import clear_cache

try:
    from anvil.history import Location

except ImportError:

    from urllib.parse import parse_qs, urlparse

    def decode_search_params(url):
        query = urlparse(url).query
        params = parse_qs(query)
        decoded_params = {k: v[0] for k, v in params.items()}
        return decoded_params

    class Location(object):
        def __init__(self, path, search="?", hash="#", state=None, key=None):
            self.path = path
            self.search = search
            self.hash = hash
            self.state = state
            self.key = key

        @property
        def search_params(self):
            return decode_search_params(self.search)


articles = [
    {"id": id, "name": f"Article {id}", "body": "Lorem ipsum"} for id in range(1, 200)
]


def get_page(page):
    return articles[3 * (page - 1) : 3 * page]


@pytest.fixture
def routes():
    class HomeRoute(Route):
        path = "/"
        form = "HomeForm"

    class ArticlesRoute(Route):
        path = "/articles"
        form = "ArticlesForm"

        def parse_search_params(self, search_params):
            page = search_params.get("page", 1)
            try:
                page = int(page)
            except ValueError:
                page = 0
            return {**search_params, "page": page}

        def loader_deps(self, **loader_args):
            page = loader_args.get("search_params", {}).get("page", 1)
            return {"page": page}

        def loader(self, **loader_args):
            # usually this would be a server call
            page = loader_args.get("deps", {}).get("page", 1)
            return get_page(page)

    class ArticleRoute(Route):
        path = "/articles/:id"
        form = "ArticleForm"
        stale_time = 0.1

        def parse_path_params(self, path_params):
            id = path_params.get("id", 1)
            try:
                id = int(id)
            except ValueError:
                id = 0
            return {"id": id}

        def loader(self, **loader_args):
            sleep(self.stale_time / 2)
            id = loader_args.get("path_params", {}).get("id", 1)
            return {**articles[id - 1]}
    
    yield [HomeRoute, ArticlesRoute, ArticleRoute]

    sorted_routes.clear()
    clear_cache()
