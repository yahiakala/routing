import anvil
from anvil.designer import get_design_component
from anvil.js import get_dom_node

_DefaultLink = get_design_component(anvil.Link)


class DefaultLink(_DefaultLink):
    def __init__(self, href=None, **properties):
        self._active = False
        super().__init__(url=href, **properties)
        self._d = get_dom_node(self)
        self._d.addEventListener("click", self._handle_click, True)

    def _handle_click(self, e):
        e.stopImmediatePropagation()
        self.raise_event("click", event=e)

    @property
    def href(self):
        return self.url

    @href.setter
    def href(self, value):
        self.url = value

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.role = "active" if value else None


BaseAnchor = DefaultLink
BaseNavLink = DefaultLink

try:
    from m3.Link import Link as M3Link
    from m3.NavigationLink import NavigationLink as M3NavLink

    class BaseAnchor(M3Link):
        def __init__(self, href=None, **properties):
            super().__init__(url=href, **properties)

        @property
        def href(self):
            return self.url

        @href.setter
        def href(self, value):
            self.url = value

    class BaseNavLink(M3NavLink):
        def __init__(self, href=None, active=False, **properties):
            super().__init__(url=href, selected=active, **properties)

        @property
        def href(self):
            return self.url

        @href.setter
        def href(self, value):
            self.url = value

        @property
        def active(self):
            return self.selected

        @active.setter
        def active(self, value):
            self.selected = value


except ImportError:
    pass


try:
    from Mantine import utils
    from Mantine.Anchor import Anchor as BaseAnchor
    from Mantine.NavLink import NavLink as BaseNavLink

    utils.set_color_scheme("light")

except ImportError:
    pass
