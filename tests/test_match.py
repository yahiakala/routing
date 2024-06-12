from client_code.router.matcher import get_matches
from tests.deps import Location, routes


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
    assert match.search_params == {"page": 1, "foo": "bar"}

    match = get_matches(location=Location("/", "?foo=bar"))
    assert match is not None
    assert type(match.route) is HomeRoute
    assert match.search_params == {"foo": "bar"}

    match = get_matches(location=Location("/articles/123", "?foo=bar"))
    assert match is not None
    assert type(match.route) is ArticleRoute
    assert match.search_params == {"foo": "bar"}
    assert match.path_params == {"id": 123}
