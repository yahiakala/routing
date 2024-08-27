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

## Form instantiation

When a form is instantiated, the router will pass a `routing_context` property to the form. This property holds information about the current route and the current navigation context.

```python
from ._anvil_designer import IndexTemplate

from routing.router import RoutingContext

class IndexTemplate(IndexTemplate):
    def __init__(self, routing_context: RoutingContext, **properties):
        self.routing_context = routing_context
        self.init_components(**properties)

```

Adding the `RoutingContext` type definition will allow anvil to show autocompletion for the `routing_context` property.

## Caching Forms

By default, the `open_form` will NOT cache the form. This means a new instance of the form will be created every time the user navigates to the route. If you want to cache the form, you can set the `cache_form` attribute to `True` on the route.

You can set this attribute on specific routes.

```python
class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
    cache_form = True
```

Or you can set this attribute for all routes by setting the `cache_form` attribute on the `Route` class.

```python
from routing.router import Route

# override the default behavior for all routes
Route.cache_form = True

class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
```

## Not Found Form

If a route is not found, the router will call `anvil.open_form` on the matching route's not found form.

If no not found form is defined, the router will raise a `NotFound` exception, which will be caught by Anvil's exception handler.

```python

from routing.router import Route

# you probably want to define a default not found form
Route.not_found_form = "Pages.NotFound"

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



