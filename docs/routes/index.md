---
weight: -8
---

# Route Class

The `Route` class is used to define routes for your app. When a user navigates to a path, the router will look for a matching route. The router will call `anvil.open_form` on the matching route's form.

```python
# routes.py
from routing.router import Route

class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"

class AboutRoute(Route):
    path = "/about"
    form = "Pages.About"

class ContactRoute(Route):
    path = "/contact"
    form = "Pages.Contact"
```

The above code can use the `Route.create()` method for convenience:

```python
# routes.py
from routing.router import Route

IndexRoute = Route.create(path="/", form="Pages.Index")
AboutRoute = Route.create(path="/about", form="Pages.About")
ContactRoute = Route.create(path="/contact", form="Pages.Contact")
```

## Route Attributes

`path`
: The path to navigate to. e.g. `/`, `/articles` or `/articles/:id`.

`form`
: The form to open when the route is matched. e.g. `Pages.Index`.

`error_form (optional)`
: The form to open when an error occurs. e.g. `Pages.Error`.

`not_found_form (optional)`
: The form to open when the route is not found. e.g. `Pages.NotFound`.

`pending_form (optional)`
: The form to open when the data is loading. e.g. `Pages.Loading`.

`pending_delay=1`
: The delay before showing the pending form when the data is loading.

`pending_min=0.5`
: The minimum time to show the pending form when the data is loading.

`cache_data=False`
: Whether to cache data. By default this is `False`.

`gc_time=30*60`
: The time in seconds that determines when data is released from the cache for garbage collection. By default this is 30 minutes. When data is released from the cache, any cached forms with the same `path` and `cache_deps` will also be released.

<!-- `stale_time=0`
: The time in seconds that determines when the data is stale. By default this is 0, i.e. the data is always considered stale when navigating to the route. This is only relevant when `cache_data` is set to `STALE_WHILE_REVALIDATE`. -->

`server_fn (optional str)`
: The server function to call when the route is matched. e.g. `"get_article"`. This server function will be called with the same keyword arguments as the route's `load_data` method. Note this is optional and equivalent to defining a `load_data` method the calls the same server function.

`server_silent=False`
: If `True` then the server function will be called using `anvil.server.call_s`. By default this is `False`.

## Route Methods

`before_load`
: Called before the route is matched. This method can raise a `Redirect` exception to redirect to a different route. By default this returns `None`.

`parse_query`
: should return a dictionary of query parameters. By default this returns the original query parameters.

`parse_params`
: should return a dictionary of path parameters. By default this returns the original path parameters.

`meta`
: should return a dictionary with the `title` and `description` of the page. This will be used to update the meta tags and the title of the page. By default this returns the original title and description.

`load_data`
: Called when the route is matched. The return value will be available in the `data` property of the `RoutingContext` instance. By default this returns `None`.

`load_form`
: This method is called with two arguments. The first argument is a form name (e.g. `"Pages.Index"`) or, if you are using cached forms, the cached form instance. The second argument is the `RoutingContext` instance. By default this calls `anvil.open_form` on the form.

`cache_deps`
: Caching is determined by the `path` and the return value of the `cache_deps` method. The default implementation returns the `query` dictionary. That is, a route with the same `path` and `query` will be considered to be the same route. And routes with different `query` will be considered to be different routes.

## Not Found Form

If a route is not found, the router will call `anvil.open_form` on the matching route's not found form.

If no not found form is defined, the router will raise a `NotFound` exception, which will be caught by Anvil's exception handler.

```python

from routing.router import Route

# you probably want to define a default not found form
Route.not_found_form = "Pages.NotFound"

```

```python
# Pages.NotFound
import anvil

class NotFound(NotFoundTemplate):
    def __init__(self, routing_context: RoutingContext, **properties):
        self.init_components(**properties)
        self.routing_context = routing_context
        self.label.text = f"404: No route found for {routing_context.path!r}"

    def form_show(self, **event_args):
        if anvil.app.environment.name.startswith("Debug"):
            raise self.routing_context.error

```

## Error Form

When a route throws an exception, the router will call `anvil.open_form` on the matching route's error form.

If no error form is defined, the error will be caught by Anvil's exception handler.

```python
from routing.router import Route

# Either define the error form globally
Route.error_form = "Pages.Error"


# or define the error form per route
class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
    error_form = "Pages.Error"

```

```python
# Pages.Error
import anvil

class Error(ErrorTemplate):
    def __init__(self, routing_context: RoutingContext, **properties):
        self.init_components(**properties)
        self.routing_context = routing_context
        self.label.text = (
            f"Error when navigating to {routing_context.path!r}, got {routing_context.error!r}"
        )

    def form_show(self, **event_args):
        if anvil.app.environment.name.startswith("Debug"):
            raise self.routing_context.error

```

## Ordering Routes

The router will try to match routes in the order they are defined.

```python
from routing.router import Route

class AuthorsRoute(Route):
    path = "/authors"
    form = "Pages.Authors"

class NewAuthorRoute(Route):
    path = "/authors/new"
    form = "Pages.NewAuthor"

class AuthorRoute(Route):
    path = "/authors/:id"
    form = "Pages.Author"

```

In the above example, it's important that the `NewAuthorRoute` comes before the `AuthorRoute` in the list of routes. This is because `/authors/new` is a valid path for the `AuthorRoute`, so the router would successfully match the route and open the form.

## Server Routes

When a user navigates to a url directly, the router will match routes on the server.

When you import your routes in server code, the router will automatically create a server route for each route.

```python
# ServerRoutes.py
from . import routes
```

Under the hood this will look something like:

```python
# ServerRoutes.py
from . import routes

# pseudo code - for illustration only
for route in Routes.__subclasses__():
    if route.path is None:
        continue

    @anvil.server.route(route.path)
    def server_route(**params):
        ...
        # return a response object that will open the form on the client

```
