# Query

Query parameters are encoded in a URL following a `?`, e.g. `/dashboard?tab=sales&page=1`.
Query parameters may be referred to by different names, e.g. search, search params, query params, etc.

In this routing library, we will refer to `query` as a dictionary of query parameters.
And a `query string` will be the URL-encoded version of the `query`.

The `query` is best used to encode the state of the page.
For example, if you have a dashboard page with a tab component, you can use the query to encode the active tab.

## Navigating

Let's say you have a dashboard page with a tab component.
The tab component has 2 tabs, income and expenses.

```python
from ._anvil_designer import DashboardTemplate
from routing.router import navigate, RoutingContext

class Dashboard(DashboardTemplate):
    def __init__(self, routing_context: RoutingContext, **properties):
        self.init_components(**properties)
        self.routing_context = routing_context
        routing_context.add_event_handler("query_changed", self.on_query_change)
        routing_context.raise_init_events() # raises the query_changed event

    def on_query_change(self, **event_args):
        query = self.routing_context.query
        self.tab_1.value = query.get("tab", "income")

    def tab_changed(self, **event_args):
        tab_value = self.tab_1.value
        navigate(query={"tab": tab_value})
```

Note that in the `tab_changed` event handler, we are navigating to the same path, and so, we don't need to include the `path` in the `navigate` call.
If we want to be explicit, we can use `path="./"` or `path="/dashboard"`.

By default, if the query parameters change, a new instance of the form will be loaded (even if `cache_form` is set to `True`). See `cache_deps` below for more details.
When the query parameters change, we can listen for the `query_changed` event and update our page state accordingly.

## Parsing Query Parameters

Since query parameters are encoded in the URL, we may need to decode them.
It's also generally a good idea to ignore unknown query parameters and provide sensible defaults if any are missing or incorrect. This provides a better user experience.

```python
from routing.router import Route

class DashboardRoute(Route):
    path = "/dashboard"
    form = "Pages.Dashboard"

    def parse_query(self, query):
        valid_tabs = ["income", "expenses"]
        tab = query.get("tab", "income")
        if tab not in valid_tabs:
            tab = "income"

        return {"tab": tab}
```

### Using a query validator

You can use a validator library. And if the validator has a `parse` method, it can be used as the `parse_query` attribute.

```python
from anvil_extras import zod as z

class DashboardRoute(Route):
    path = "/dashboard"
    form = "Pages.Dashboard"

    parse_query = z.typed_dict({
        "tab": z.enum(["income", "expenses"]).catch("income")
    })
```

## Query encoding

The routing library can encode any JSON-able object as a query parameter.
Where a query parameter is a `str`, `int`, `float`, `bool` or `None`, this will be flat.

e.g. `?foo=bar&baz=1&eggs=true` will be decoded as `{"foo": "bar", "baz": 1, "eggs": True}`.

!!! note

    If you have numbers in your query parameters, but these should actually be strings, you can convert these to `str` in your `parse_query` method.

For nested, JSON-able objects, i.e. `lists` and `dicts`, the routing library will encode the object as a JSON string in the query string.

e.g. `foo=%5B1%2C+%22a%22%2C+true%5D'` will be decoded as `{"foo": [1, "a", true]}`.

## Loading a new instance of a form

By default, the routing library will load a new instance of a form when the query parameters change.

If you do NOT wish to load a new instance of a form when certain query parameters change, you can override the `cache_deps` method.

This method should return a `dict` of dependencies, which determine when a form and its data should be loaded from `cache`. The return value from `cache_deps` should be JSON-able.

```python
from routing.router import Route

class DashboardRoute(Route):
    path = "/dashboard"
    form = "DashboardForm"
    cache_form = True

    def cache_deps(self, **loader_args):
        # this form is cached uniquely by the `path` only - there are no `query` dependencies
        # i.e. if the `tab` changes, we keep the same instance of the form
        return None
```

For more details on `cache_deps`, see the data loading section.
