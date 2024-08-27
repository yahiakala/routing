# Query

Query parameters are encoded in a url following a `?`, e.g. `/dashboard?tab=sales&page=1`.
Query parameters may be referred to by different names, e.g. search, search params, query params, etc.

In this routing library we will refer to `query` as a dictionary of query parameters.
And a `query string` will be the url encoded version of the `query`.

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
        self.routing_context = routing_context
        self.routing_context.add_event_handler("query_changed", self.on_query_change)
        self.set_tab_from_query()
        self.init_components(**properties)

    def set_tab_from_query(self, **event_args):
        query = self.routing_context.query
        self.tab_1.value = query.get("tab", "income")

    def tab_changed(self, **event_args):
        tab_value = self.tab_1.value
        navigate(query={"tab": tab_value})


```

Note that in the `tab_changed` event handler, we are navigating to the same page, and so, we don't need to include the `path` in the `navigate` call.
If we want to be explicit, we can use `path="./"` or `path="/dashboard"`.

By default, if the query parameters change, the page will not be reloaded.
When the query parameters change, we can listen for the `query_changed` event and update our page state accordingly.

## Parsing Query Parameters

Since query parameters are encoded in the url, we may need to decode them.
It's also generally a good idea to ignore unknown query parameters and provide sensible defaults if any are missing, or incorrect. This provides a better user experience.

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

The routing library can encode any json-able object as a query parameter.
Where a query parameter is a `str`, `int`, `float`, `bool` or `None` this will be flat.

e.g. `?foo=bar&baz=1&eggs=true` will be decoded as `{"foo": "bar", "baz": 1, "eggs": True}`.

!!! note

    If you have numbers in your query parameters, but these should actually be strings, you can convert these to `str` in your `parse_query` method.

For nested, json-able objects, i.e. `lists` and `dicts`, the routing library will encode the object as a json string.

## Loading a new instance of a form

By default the routing library will not load a new instance of a form when the query parameters change.

If you wish to load a new instance of a form when certain query parameters change, you can use the `loader_deps` method.

This method should return a `dict` of dependencies, which determine when a form and it's data should be loaded. The return value from `loader_deps` should be json-able.


```python

from routing.router import Route

class DashboardRoute(Route):
    path = "/dashboard"
    form = "DashboardForm"

    def loader_deps(self, **loader_args):
        # this ensures that whenever the `tab` changes a new instance of the form is loaded
        query = loader_args["query"]
        return {"tab": query["tab"]}

```

For more details on `loader_deps` see the data loading section.

