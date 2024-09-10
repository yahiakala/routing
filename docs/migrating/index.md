# Migrating

## From an app that navigates with `anvil.open_form`

Define your routes. If you are not using `params` in any routes you should be able to replace all calls to `anvil.open_form` with `router.open_form`. To begin with make sure to set `cached_forms` to `False`. As you decide certain routes should have `params` you will need to replace `router.open_form` with `router.navigate`. The keyword arguments to `open_form` will be a dictionary you pass to the `form_properties` argument of `navigate`.

A common gotcha will be that a Form could previously rely on the `item` property always being passed to the form. But this will not be the case if a user navigates directly to the form. In this case the `item` property will be `None` and you will have to fetch the item based on the `routing_context`.

## From `anvil_extras.routing` (`HashRouting`)

Define your routes. Each route definition will be similar to the hash routing `@route` decorator.

By default the routing library will call `anvil.open_form` on the matching route's form. You can make the routing library behave more like hash routing by setting `load_form_mode` to `TEMPLATE_WITH_CONTAINER`.

If you have a single template in your hash routing app, then set the `Route.template = "MyTemplate"`.

If you have multiple templates, then you can either set the `template` attribute on individual routes, or define a `get_template` method on the `Route` class.

```python

def get_template(**loader_args):
    if anvil.users.get_user():
        return "MainTemplate"
    else:
        return "LoginTemplate"

Route.get_template = staticmethod(get_template)

```

Instead of calling hash routing's `set_url_hash` method, use the `navigate` function.

If the route decorator uses `full_width_row` you should configure the `Route.template_container_properties` attribute.

```python

from routing.router import Route, TEMPLATE_WITH_CONTAINER

Route.load_form_mode = TEMPLATE_WITH_CONTAINER
Route.template = "MainTemplate"

class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
    template_container_properties = {"full_width_row": True}

```
