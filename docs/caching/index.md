# Caching

The routing library provides simple caching mechanisms for forms and data.
By default, the routing library will **NOT** cache any forms or data.

## Clearing Cache

To clear the cache, you can call the `clear_cache` function.

```python
from routing import router
router.clear_cache()
```

## Form Caching

To override the default behavior, you can set the `Route.cache_form` attribute to `True`. This will cause the routing library to cache all forms.

```python
from routing.router import Route
Route.cache_form = True
```

You can also set this attribute on specific routes.

```python
class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
    cache_form = True
```

## Data Caching

The routing library will cache data that was loaded by the `load_data` method. If you are not using the `load_data` method, then you can skip this section. For more details see the [Data Loading](/data-loading) section.

The data caching behavior is determined by the `cache_data` attribute on the route.

!!! Note

    If there is a `load_data` method, and there is no data in the cache, the the form will not be instantiated until the `load_data` method returns a value.

!!! Caching Forms with data loaders

    If you are using `load_data` method and `cache_form` is set to `True`, then load_data method will not be called if there is an existing cached form. If you are using `STALE_WHILE_REVALIDATE` mode, we would recommend setting `cache_form` to `False` so that the `load_data` method is called with the data is stale.

### No Cache

By default, the routes use the `NO_CACHE` mode, i.e. data will not be cached.

### Cache First

In `CACHE_FIRST` mode, the data will always be loaded from the cache if it is available.

### Network First

In `NETWORK_FIRST` mode, the data will always be loaded from the `load_data` when the user navigates to a route. However, if the `load_data` method raises an `AppOfflineError`, the data will be loaded from the cache.

### Stale While Revalidate

A more advanced mode is `STALE_WHILE_REVALIDATE`. In this mode, the data will be loaded from the cache, and then loaded in the background from the server, if the data is stale. If there is no data in the cache, then the form will not be instantiated until the `load_data` method returns a value.

```python
from routing.router import Route, STALE_WHILE_REVALIDATE

Route.cache_data = STALE_WHILE_REVALIDATE

```

Or you can set this attribute on specific routes.

```python
class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
    cache_data = STALE_WHILE_REVALIDATE
```

If you are using the `STALE_WHILE_REVALIDATE` mode, then you can customize the caching behavior by setting the `Route.stale_time` attribute. By default this is `0` seconds. i.e. the data is always considered stale when navigating to the route.

When the data is stale, the form will be instantiated with the stale data. The route's `load_data` method will be called in the background, and when the `load_data` method returns a value, the `routing_context` will be updated with the new data and raise the `"data_loaded"` event.

```python
from routing import router

class ArticlesForm(ArticlesFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.init_components(**properties)
        self.routing_context = routing_context
        self.routing_context.add_event_handler("data_loaded", self.on_data_loaded)
        self.routing_context.raise_init_events()

    def on_data_loaded(self, **event_args):
        self.repeating_panel.items = self.routing_context.data

```

## Caching keys

The routing library will cache forms by the key. The key is a combination of the path, and the dictionary returned by the `cache_deps` method. By default the `cache_deps` method returns the `query` dictionary.

## Invalidating Cache

If you want to invalidate the cache, you can call the `invalidate` function. Invalidating the cache will remove data and forms from the cache.

```python
from routing import router
router.invalidate(path="/articles")
```

The call signature for `invalidate` is:

```python

invalidate(*, path=None, deps=None, exact=False)
invalidate(path, **kws)
invalidate(routing_context, **kws)

```

`path`

: The path to invalidate.

`deps`

: The dependencies to invalidate. These are the same dependencies that are returned by the `cache_deps` method.

`exact`

: If `True` then the path and deps must match exactly. If `False` (the default) then any path or deps that are a subset of path and deps arguments will be invalidated.

## Partial Invalidation

```python

from routing.router import Route

class ArticlesRoute(Route):
    path = "/articles"
    form = "Pages.Articles"

class ArticleRoute(Route):
    path = "/articles/:id"
    form = "Pages.Article"

```

In the above example if you call `invalidate("/articles", exact=True)` then data and forms associated with the `ArticlesRoute` will be invalidated. If you call `invalidate("/articles", exact=False)` then data and forms associated with the `ArticlesRoute` and all cached `ArticleRoute`s will be invalidated since the `ArticleRoute` path is a subset of the `ArticlesRoute` path.

```python

from routing.router import Route

class ArticlesRoute(Route):
    path = "/articles"
    form = "Pages.Articles"

    def cache_deps(self, **loader_args):
        return {"page": loader_args["query"]["page"]}

    def parse_query(self, query):
        return {**query, "page": int(query.get("page", 1))}

```

In the above example the data is cached depending on the `page` query parameter. If you call `invalidate("/articles")` then all data associated with all pages will be invalidated. A deps value of `{"page": 1}` is considered a subset of an empty deps argument. If you call `invalidate("/articles", exact=True)` then no data will be invalidated, since there is no match. Calling `invalidate("/articles", deps={"page": 1})` will invalidate only the data for the first page.

## Invalidating Contexts

A routing context also has an `invalidate` method for convenience.

```python

from routing import router

class ArticleForm(ArticleFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        self.init_components(**properties)

    def delete_button_click(self, **event_args):
        self.remove_from_parent()
        self.routing_context.invalidate(exact=True)

```
