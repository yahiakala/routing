---
weight: -9
---

# Navigation

There are two ways to navigate. The first is with the `navigate` function, and the second is with a [navigation component](/navigating/Navigation%20Components).

## Navigating with `navigate`

The `navigate` function is a function that you will likely call from a click handler.

```python
from routing.router import navigate

class Form(FormTemplate):
    def nav_button_click(self, **event_args):
        navigate(path="/articles/:id", params={"id": 123})
```

### Call Signatures

-   `navigate(*, path=None, params=None, query=None, hash=None, replace=False, nav_context=None, form_properties=None)`
    _use keyword arguments only_
-   `navigate(path, **kws)`
    _the first argument can be the path_
-   `navigate(url, **kws)`
    _the first argument can be a URL_
-   `navigate(routing_context, **kws)`
    _the first argument can be a routing context_

### Arguments

`path`
: The path to navigate to. e.g. `/articles/123` or `/articles` or `/articles/:id`. The path can be relative `./`. If not set, then the path will be the current path.

`params`
: The params for the path. e.g. `{"id": 123}`

`query`
: The query parameters to navigate to. e.g. `{"tab": "income"}`. This can be a function that takes the current query parameters as an argument and returns the new query parameters. If you provide a query function, avoid modifying the query parameters directly, instead return a new dictionary.

```python

def on_button_click(self, **event_args):
    def query(prev):
        return {**prev, "open": not prev.get("open", False)}
    navigate(query=query)

```

`hash`
: The hash to navigate to.

`replace`
: If `True`, then the current URL will be replaced with the new URL (default is `False`).

`nav_context`
: The nav context for this navigation.

`form_properties`
: The form properties to pass to the form when it is opened.

### Use of `form_properties`

The `form_properties` is a dictionary that is passed to the `open_form` function. A common use case is to pass the form's `item` property. Note that if you are relying on `form_properties`, you will always need to account for `form_properties` being an empty dictionary when the user navigates by changing the URL directly.

```python
from routing import router

class RowTemplate(RowTemplateTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

    def button_click(self, **event_args):
        router.navigate(
            path="/articles/:id",
            params={"id": self.item["id"]},
            form_properties={"item": self.item}
        )
```

And then in the `/articles/:id` route:

```python
from routing import router

class ArticleForm(ArticleFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        if properties.get("item") is None:
            # The user navigated directly
            # to the form by changing the URL
            article_id = routing_context.params["id"]
            properties["item"] = anvil.server.call("get_article", article_id)

        self.init_components(**properties)
```

### Use of `nav_context`

The `nav_context` is a dictionary that is passed to the `navigate` function. A use case for this is to pass the previous routing context to the next routing context. This is useful when you want to navigate to a new route but want to preserve the previous route's data, particularly if the previous route uses query parameters that determine the state of the form.

```python
from routing import router

def on_button_click(self, **event_args):
    current_context = router.get_routing_context()
    router.navigate(path="/foo", nav_context={"prev_context": current_context})
```

And then in the `/foo` route:

```python
from routing import router

class FooForm(FooFormTemplate):
    def __init__(self, routing_context: router.RoutingContext, **properties):
        self.routing_context = routing_context
        self.init_components(**properties)

    def cancel_button_click(self, **event_args):
        prev_context = self.routing_context.nav_context.get("prev_context")
        if prev_context is not None:
            router.navigate(prev_context)
        else:
            # No nav-context - the user navigated directly to the form by changing the URL
            router.navigate(path="/")
```
