# Overview 
This documentation provides an overview of the API for the routing library.

## Installation
You can use this library as a third party Anvil dependency with the code `ABC123`.

## Quick Start
Clone the following Anvil app:
https://anvil.works/app/ABC123

Or create a new app from Anvil app

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

```python
# startup.py
from routing.router import launch
from .import routes

if __name__ == "__main__":
    launch()
```

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

Inside your Server code, create a server module that imports the `routes` module.

```python
# ServerRoutes.py
from . import routes
```

You should now be able to run the app and navigate to different pages by changing the URL in the browser.








### Initializing the Router
How to initialize the router.

### Defining Routes
How to define routes.

### Handling Routes
How to handle and process routes.

## API Reference

### Route Class
Details about the `Route` class and its methods, if applicable.

### Navigation
Details about navigating.

## Examples
Some basic examples of how to use the routing library.
