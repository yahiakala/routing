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

You can also set this attribute on specific routes.

```python
class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
    cache_form = True
```


## Data Caching

The routing library will cache data that was loaded by the `loader` method. If you are not using the `loader` method, then you can skip this section. For more details see the [Data Loading](/data-loading) section.

The data caching behavior is determined by the `cache_mode` attribute on the route.

!!! Note

    If there is a `loader` method, and there is no data in the cache, then the data will be loaded from the server before the form is instantiated.


### Network First

By default, the routing library uses the `NETWORK_FIRST` mode. In this mode, the data will always be loaded from the server. However, if there is an `AppOfflineError`, the data will be loaded from the cache.

### Stale While Revalidate

A more advanced mode is `STALE_WHILE_REVALIDATE`. In this mode, the data will be loaded from the cache, and then loaded in the background from the server, if the data is stale. If there is no data in the cache, then the data will be loaded from the server.


```python
from routing.router import Route, STALE_WHILE_REVALIDATE

Route.cache_mode = STALE_WHILE_REVALIDATE

```

Or you can set this attribute on specific routes.

```python
class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
    cache_mode = STALE_WHILE_REVALIDATE
```

If you are using the `STALE_WHILE_REVALIDATE` mode, then you can customize the caching behavior by setting the `Route.stale_time` attribute. By default this is `0` seconds. i.e. the data is always considered stale.

Since data can be loaded in the background, it is necessary to subscribe to the `data_loaded` event, and possibly the `data_error`, and `data_loading` events.

```python
from routing import router

class ArticlesForm(ArticlesFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        self.routing_context.add_event_handler("data_loaded", self.on_data_loaded)
        self.init_components(**properties)
        self.on_data_loaded()

    def on_data_loaded(self, **event_args):
        self.repeating_panel.items = self.routing_context.data

```

## Caching keys

The routing library will cache forms by the key. The key is a combination of the path, and the dictionary returned by the `loader_deps` method.


## Invalidating Cache

!!! TODO

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

: The dependencies to invalidate. These are the same dependencies that are returned by the `loader_deps` method.

`exact`

: If `True` then the path and deps must match exactly. By default this is `False`. If `False` then any path or deps that are a subset of path and deps arguments will be invalidated.

`reload`

: If `True` then the data will be re-fetched from the server in the background. By default this is `False`.


A routing context also has an `invalidate` method for convenience.

```python

from routing import router

class ArticleForm(ArticleFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        self.init_components(**properties)

    def delete_button_click(self, **event_args):
        self.remove_from_parent()
        self.routing_context.invalidate()
        ## or perhaps you want to reload the data for the parent route

```