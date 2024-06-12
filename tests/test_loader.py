from client_code.router.loader import load_data
from time import sleep
from client_code.router.matcher import get_matches
from tests.deps import routes, Location, get_page

def test_loader(routes):
    [HomeRoute, ArticlesRoute, ArticleRoute] = routes

    match_1 = get_matches(location=Location("/articles/123"))
    assert match_1 is not None
    assert type(match_1.route) is ArticleRoute
    assert match_1.path_params == {"id": 123}
    assert match_1.search_params == {}

    match_2 = get_matches(location=Location("/articles/42"))
    assert match_2 is not None
    assert type(match_2.route) is ArticleRoute
    assert match_2.path_params == {"id": 42}
    assert match_2.search_params == {}

    data_1_0 = load_data(match_1)
    data_2_0 = load_data(match_2)
    sleep(.1)
    # time is now stale - we use the cached data then fetch in the background
    data_1_1 = load_data(match_1)
    data_2_1 = load_data(match_2)
    sleep(.1)
    data_1_2 = load_data(match_1)
    data_2_2 = load_data(match_2)
    assert data_1_0["id"] == 123
    assert data_1_0["name"] == "Article 123"
    assert data_1_0["body"] == "Lorem ipsum"
    assert data_1_0 is data_1_1
    assert data_1_0 is not data_1_2

    assert data_2_0["id"] == 42
    assert data_2_0 is data_2_1
    assert data_2_0 is not data_2_2

    articles_match_1 = get_matches(location=Location("/articles", "?page=1"))
    assert articles_match_1 is not None
    assert type(articles_match_1.route) is ArticlesRoute
    assert articles_match_1.search_params == {"page": 1}

    articles_match_2 = get_matches(location=Location("/articles", "?page=2"))
    assert articles_match_2 is not None
    assert type(articles_match_2.route) is ArticlesRoute
    assert articles_match_2.search_params == {"page": 2}

    data_1_0 = load_data(articles_match_1)
    data_2_0 = load_data(articles_match_2)
    sleep(.1)
    # time is now stale - we use the cached data then fetch in the background
    data_1_1 = load_data(articles_match_1)
    data_1_2 = load_data(articles_match_1)

    assert data_1_0 != data_2_0
    assert get_page(1) == data_1_0
    assert get_page(2) == data_2_0

    assert data_1_0 is data_1_1
    assert data_1_0 is not data_1_2

