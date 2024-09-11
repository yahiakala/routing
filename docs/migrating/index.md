# Migrating

## From an app that navigates with `anvil.open_form`

Define your routes. If you are not using `params` in any routes you should be able to replace all calls to `anvil.open_form` with `router.open_form`. To begin with make sure to set `cached_forms` to `False`. As you decide certain routes should have `params` you will need to replace `router.open_form` with `router.navigate`. The keyword arguments to `open_form` will be a dictionary you pass to the `form_properties` argument of `navigate`.

A common gotcha will be that a Form could previously rely on the `item` property always being passed to the form. But this will not be the case if a user navigates directly to the form. In this case the `item` property will be `None` and you will have to fetch the item based on the `routing_context`.

## From `anvil_extras.routing` (`HashRouting`)

Define your routes. Each route definition will be similar to the hash routing `@route` decorator.

By default, when a route subclasses from `Route` the routing library will call `anvil.open_form` on the matching route's form. For hash routing apps, this is not what you want. Instead you should subclass from `TemplateWithContainerRoute` and set the `template` attribute to the template form.

```python

from routing.router import TemplateWithContainerRoute as BaseRoute

BaseRoute.template = "MainTemplate"

class IndexRoute(BaseRoute):
    path = "/"
    form = "Pages.Index"

```

If you have a single template in your hash routing app, then set the `BaseRoute.template = "MyTemplate"`.

If you have multiple templates, then you can either set the `template` attribute on individual routes, or define a `get_template` method on the `Route` class.

#### `set_url_hash`

Instead of calling hash routing's `set_url_hash` method, use the `navigate` function.

#### `full_width_row`

If the route decorator uses `full_width_row` you should configure the `Route.template_container_properties` attribute.

```python

from routing.router import TemplateWithContainerRoute as BaseRoute

BaseRoute.template = "MainTemplate"

class IndexRoute(BaseRoute):
    path = "/"
    form = "Pages.Index"
    template_container_properties = {"full_width_row": True}

```

