---
weight: -9.8
---

# How It Works

## Routing Basics

As an app developer, you will need to define routes for your app.
When the URL changes, the router will look for a matching route.
The router will attempt to match routes in the order they are defined.

When a route is found, the router will call the route's `before_load` method.
If the `before_load` method raises a `Redirect`, the router will navigate to the redirected URL.

If the route has a `load_data` method, it will be called, and the return value will be available as the `data` property on the `RoutingContext`.

Once the `load_data` method has been called, the router will call the route's `load_form` method. A `routing_context` will be passed to this method. By default, the `load_form` method will call `anvil.open_form` on the matching route's form, with `routing_context` passed as a keyword argument.

## Caching

There are two types of caching: form caching and data caching.

If a form is cached, instead of creating a new instance, the router will call the route's `load_form` method with the cached form instance.

If data is cached, the router will only call the `load_data` method if the data is stale. See the [Caching](/caching) section for more details.

## Server vs Client Routing

The above process will occur on the server if the user navigates directly to a URL (the initial page request). If the user is navigating from within the app, then routing will happen on the client.
