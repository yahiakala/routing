import pytest
from urllib.parse import parse_qs, urlparse


from client_code.router.routes import Route, sorted_routes
from client_code.router.matcher import get_matches


from urllib.parse import parse_qs, urlparse

def decode_search_params(url):
    query = urlparse(url).query
    params = parse_qs(query)
    decoded_params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
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


@pytest.fixture
def routes():
    print("HERE")
    
    class HomeRoute(Route):
        path = "/"
        form = "HomeForm"

    class ArticlesRoute(Route):
        path = "/articles"
        form = "ArticlesForm"
    
    class ArticleRoute(Route):
        path = "/articles/:id"
        form = "ArticlesForm"
        def parse_path_params(self, path_params):
            id = path_params.get("id", 0)
            try:
                id = int(id)
            except ValueError:
                id = 0
            return {"id": id}


    yield [HomeRoute, ArticlesRoute, ArticleRoute]

    sorted_routes.clear()

def test_match(routes):
    [HomeRoute, ArticlesRoute, ArticleRoute] = routes

    match = get_matches(location=Location("/"))
    assert match is not None
    assert type(match.route) is HomeRoute

    match = get_matches(location=Location("/articles"))
    assert match is not None
    assert type(match.route) is ArticlesRoute

    match = get_matches(location=Location("/articles", "?foo=bar"))
    assert match is not None
    assert type(match.route) is ArticlesRoute
    assert match.search_params == {"foo": "bar"}

    match = get_matches(location=Location("/", "?foo=bar"))
    assert match is not None
    assert type(match.route) is HomeRoute
    assert match.search_params == {"foo": "bar"}

    match = get_matches(location=Location("/articles/123", "?foo=bar"))
    assert match is not None
    assert type(match.route) is ArticleRoute
    assert match.search_params == {"foo": "bar"}
    assert match.path_params == {"id": 123}



