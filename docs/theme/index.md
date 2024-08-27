# Theme

If you are writing a custom theme for your anvil app, you may want to use your own components for the `NavLink` and `Anchor` base classes.

The default implementation for the `NavLink` and `Anchor` base classes are:

```python

import anvil

class NavLinkBase(anvil.Link):
    def __init__(self, active=None, **properties):
        self._props = properties
        super().__init__(**properties)

    @property
    def active(self):
        return self._props.get("active")

    @active.setter
    def active(self, value):
        self._props["active"] = value
        self.role = "selected" if value else None


class AnchorBase(anvil.Link):
    pass

```

**TODO - not yet supported APIs** 

To tell the routing library to use your own base classes, you can call the anvil's `set_config` method in the preload module.

```python

# preload module

from anvil import set_config
from ...MyNavLink import MyNavLink
from ...MyAnchor import MyAnchor
set_config(nav_link=MyNavLink, anchor=MyAnchor)

```

## Existing Themes

- Mantine
- M3 **TODO**

!!! Note

    If you are using multiple themes that set the `NavLink` and `Anchor` base classes, then the last theme to set the base classes will be used.
