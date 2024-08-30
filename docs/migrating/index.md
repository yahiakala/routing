# Migrating

## From an app that navigates with `anvil.open_form`

Define your routes. If you are not using `params` in any routes you should be able to replace all calls to `anvil.open_form` with `router.open_form`. To begin with make sure to set `cached_forms` to `False`. As you decide certain routes should have `params` you will need to replace `router.open_form` with `router.navigate`. The keyword arguments to `open_form` will be a dictionary you pass to the `form_properties` argument of `navigate`. 

A common gotcha will be that a Form could previously rely on the `item` property always being passed to the form. But this will not be the case if a user navigates directly to the form. In this case the `item` property will be `None` and you will have to fetch the item based on the `routing_context`.

## From `anvil_extras.routing` (`HashRouting`)

There is no clear migration path from `HashRouting` to `routing`. One major obstacle for migration is that `HashRouting` keeps the template the same and changes the component of the template's `content_panel`. `routing` calls `anvil.open_form` on the matching route's form.

When using the `routing` library it is recommended to use layouts. To begin the process of migrating you would need to turn any templates into layouts. Simply add a `slot` into the template's `content_panel`. The challenge comes when trying to convert `HashRouting` route Form's to use the template layout. There is no simple way to do this.


