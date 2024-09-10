## Forms

The `Route.load_form` method is called when the route is matched. The default implementation depends on the `load_form_mode` attribute on the route.

### LAYOUTS

`Route.load_form_mode = LAYOUTS` is the default mode. In this mode, the `load_form` method will call `anvil.open_form` on the matching route's form.

### TEMPLATE_WITH_CONTAINER

`Route.load_form_mode = TEMPLATE_WITH_CONTAINER` navigates by opening a template form, and then adding the form to the template's container. By default the container is the `content_panel` attribute of the template. The container can be configured by setting the `Route.template_container` attribute.

The template form is determined by the `Route.template` attribute or the `Route.get_template` method. A `get_template` method is useful if you have multiple templates, and you want to determine which template to open based on the current path or query.

A template form can be a string or an instance of an `anvil.Component`.

If you are using this mode, it is common to want some of your forms to use container properties, e.g. `full_width_row=True`. You can set the `Route.template_container_properties` attribute to a dictionary of container properties.

```python

from routing.router import Route, TEMPLATE_WITH_CONTAINER

Route.load_form_mode = TEMPLATE_WITH_CONTAINER
Route.template = "MainTemplate"
Route.template_container = "content_panel" # this is the default

class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"
    template_container_properties = {"full_width_row": True}

```

