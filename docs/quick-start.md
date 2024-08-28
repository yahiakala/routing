# Quick Start

## From a Clone

Clone the following Anvil app:
https://anvil.works/app/ABC123

## From a New App

Create a new app.

### Client Code Structure

The client code structure should look like this:

```
- Layouts (Package)
    - Main (Form - ensure you tick "Use as layout")
- Pages (Package)
    - Index (Form choosing Layouts.Main as the layout)
    - About (Form choosing Layouts.Main as the layout)
    - Contact (Form choosing Layouts.Main as the layout)
- routes (Module)
- startup (Module)
```

### Startup Module

```python
# startup.py
from routing.router import launch
from .import routes

if __name__ == "__main__":
    launch()
```

### Routes Module

```python
# routes.py
from routing.router import Route

class IndexRoute(Route):
    path = "/"
    form = "Pages.Index"

class AboutRoute(Route):
    path = "/about"
    form = "Pages.About"

class ContactRoute(Route):
    path = "/contact"
    form = "Pages.Contact"
```

### Server Routes Module

Inside your Server code, create a server module that imports the `routes` module.

```python
# ServerRoutes.py
from . import routes
```

You should now be able to run the app and navigate to different pages by changing the URL in the browser.

### Navigation

In `Layouts.Main`, include a `SideBar` and add 3 `NavLink` components.
(The `NavLink` component should come from the routing library)

Ensure the nav links have the following properties set:

-   The first `NavLink` should have the `path="/"`.
-   The second `NavLink` should have the `path="/about"`.
-   The third `NavLink` should have the `path="/contact"`.

Add a title `slot` to the `Layouts.Main` form. And inside `Pages.Index`, add a label component to the title slot with the `text` property set to `"Home"`. Do the same for `Pages.About` and `Pages.Contact`.

You should now be able to navigate using the side bar nav links. 