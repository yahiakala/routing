# Navigation Components

A Navigation Component is useful over a Button with a click handler because it supports `ctr/cmd` clicking a route to open in a new tab, and should provide the correct href value for the browser.

The routing library provides two Navigation Components:

-   [NavLink](#navlink)
-   [Anchor](#anchor)

Navigation Components by default are subclasses of the `Anvil.Link` component. But this can be customized. See [Themes](/theme) for details.

## NavLink

The NavLink component is a link that you will likely use in your main layout's sidebar. The routing library will set the `active` property on the NavLink to `True` when the NavLink's properties match the current routing context.

If you are using the default NavLink component, then `active` means it will set it's `role` property to `selected`. If the NavLink component is not the default, then how the `active` property behaves is determined by the Base class of the NavLink component.

### Navigation Attributes

`path`

: The path to navigate to. e.g. `/articles/123` or `/articles` or `/articles/:id`. The path can be relative `./`. If not set then the path will be the current path.

`params`

: The params for the path. e.g. `{"id": 123}`

`query`

: The query parameters to navigate to. e.g. `{"tab": "income"}`

`form_properties`

: The form properties to pass to the form when it is opened.

`nav_context`

: The nav context to for this navigation.

`hash`

: The hash to navigate to.

!!! Tip

    If you want to set `params` or `query` in the designer, you can use the data binding feature of the designer.

    ![Data Binding](/img/screenshots/data-binding.png)

### Active State

`active`

: The active state of the NavLink. You probably don't want to set this. The routing library will set it to `True` when the NavLink's properties match the current routing context.

`exact_path`

: If `True` then the path must match exactly. By default this is `False`. Which means a NavLink with a path of `/articles` will match the path `/articles`, `/articles/123` and `/articles/123/456`.

`exact_query`

: If `True` then the query must match exactly. By default this is `False`.

`exact_hash`

: If `True` then the hash must match exactly. By default this is `False`.

You can set most properties in code or in the designer. In the designer, it is recommended to set `query` properties by using data bindings.

## Anchor

Anchor is a link that you can use inline, or use as a container for other components. Unlike the NavLink, the Anchor component has no `active` property.
