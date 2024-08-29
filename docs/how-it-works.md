---
weight: -9
---
# How It Works


## Routing Basics 

As an app developer, you will need to define routes for your app.
When the url changes, the router will look for a matching route.
The router will try to match routes in the order they are defined.

When a route is found, the router will call the route's `before_load` method.
If the `before_load` method raises a `Redirect`, the router will navigate to the redirected url.

If the route has a `loader` method, it will be called and the return value will be available as the `data` property on the `RoutingContext`.

Once the `loader` method has been called, the router will call `open_form` on the matching route's form. A `routing_context` will be passed to the form.


## Caching

There are two types of caching, form caching and data caching.

If a form is cached, instead of calling the `open_form` method on the matching route's form, the router will open the cached form.

If data is cached, the router will only call the `loader` method if the data is stale. Stale data is determined by the `cache_mode` attribute on the route.


## Server vs Client Routing

The above process will happen on the server, if the user navigates directly to a url (the initial page request). If the user is navigating from within the app, then routing will happen on the client.

