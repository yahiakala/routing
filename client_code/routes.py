from .router.routes import Route
from datetime import datetime


articles = [
    {"id": id, "name": f"Article {id}", "body": "Lorem ipsum"} for id in range(1, 200)
]


def get_page(page):
    return [{**a, "timestamp": datetime.now()} for a in articles[30 * (page - 1) : 30 * page]]

raise Exception("should not import me")

class HomeRoute(Route):
    path = "/"
    form = "HomeForm"

class ArticlesRoute(Route):
    path = "/articles"
    form = "ArticlesForm"
    stale_time = 3
    pending_form = "PendingForm"

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
        from time import sleep
        sleep(2)
        page = loader_args.get("deps", {}).get("page", 1)
        return get_page(page)

class ArticleRoute(Route):
    path = "/article/:id"
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