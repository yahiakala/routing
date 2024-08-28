# How It Works

As an app developer, you will need to define routes for your app.
When the url changes, the router will look for a matching route.
The router will try to match routes in the order they are defined.

When a route is found, the router will call the route's `before_load` method.
If the `before_load` method raises a `Redirect`, the router will navigate to the redirected url.

If the route has a `loader` method, the router will call the `loader` method. The `loader` method will be called according to the `cache_mode` attribute on the route.

If the route is has set `cache_form` to `True`, and there is a cached form for the route, the router will open the cached form. Otherwise, the router will call open form on the matching route's form.


The above process may happen on the server, or on the client. If the user is navigating from with the app, that is, the user is clicking a navigation component, then the router will be called on the client. If the user navigates directly to the url, by changing the url in the browser, then the router will be called on the server.


