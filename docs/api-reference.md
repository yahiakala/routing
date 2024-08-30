---
weight: -9.7
---

# Api Reference

The routing library provides the following functions, classes and attributes.
All attributes can be accessed from the `routing.router` module.

## Functions

`navigate(*, path=None, params=None, query=None, hash=None, replace=False, nav_context=None, form_properties=None)`
`navigate(path, **kws)`
`navigate(url, **kws)`
`navigate(routing_context, **kws)`
: Navigates to a new page.

`launch()`
: Launches the routing library and navigates to the first route. Call this in your startup module.

`go(n=0)`
: Navigates to the nth page in the history stack

`back()`
: Navigates back in the history stack

`forward()`
: Navigates forward in the history stack

`reload(hard=False)`
: Reloads the current page. If `hard` is `True` then the page will be reloaded from the server. If `hard` is `False` then the page will be removed from the cache and reloaded on the client.

`get_routing_context()`
: Returns the current routing context

`get_url()`
`get_url(*, path=None, params=None, query=None, hash=None, full=False)`
`get_url(path, **kws)`
`get_url(routing_context, **kws)`
: Gets the url. if no keyword arguments are passed then the current url will be returned. If `full` is `True` then the full url will be returned e.g. `http://my-app.anvil.app/articles/123?foo=bar#hash`. If `full` is `False` then the url will be relative to the base url e.g. `/articles/123?foo=bar#hash`. If no then the current page url will be returned.

`debug_logging(enable=True)`
: Enables or disables debug logging

`clear_cache()`
: Clears the cache of forms and data

`invalidate(*, path=None, deps=None, exact=False)`
: Invalidates any cached data and forms based on the path and deps.

`open_form(form, **form_properties)`
: When migrating you may be able to replace `anvil.open_form` with `router.open_form`. This will only work if you are not using `params`.

## Classes

`Route`
: The base class for all routes.

`RoutingContext`
: Provides information about the current route and navigation context. Passed to all forms instantiated by the routing library.

## Components

`NavLink.NavLink`
: A link that you will likely use in your main layout's sidebar. Has an `active` property that is set when the NavLink's navigation properties match the current routing context.

`Anchor.Anchor`
: A link that you can use inline, or use as a container for other components.

## Context Managers

`NavigationBlocker`
: A context manager that will prevent the user from navigating away during the context.

## Exceptions

`Redirect`
: Raise during a route's `before_load` method to redirect to a different route.

`NotFound`
: Raised when a route is not found for given path.
