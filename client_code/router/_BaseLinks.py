import anvil
from anvil.designer import get_design_component
from anvil.js import get_dom_node


class UrlMixin:
    def __init__(self, href=None, **properties):
        super().__init__(url=href, **properties)

    @property
    def href(self):
        return self.url

    @href.setter
    def href(self, value):
        self.url = value


BaseAnvilLink = get_design_component(anvil.Link)


class BaseAnchor(UrlMixin, BaseAnvilLink):
    def __init__(self, **properties):
        super().__init__(**properties)
        self._d = get_dom_node(self)
        self._d.addEventListener("click", self._handle_click, True)

    def _handle_click(self, e):
        e.stopImmediatePropagation()
        self.raise_event("click", event=e)


class BaseNavLink(BaseAnchor):
    def __init__(self, active=False, **properties):
        super().__init__(**properties)
        self.active = active

    @property
    def active(self):
        return self.role == "active"

    @active.setter
    def active(self, value):
        self.role = "active" if value else None


try:
    from m3._Components.Link import Link as M3Link
    from m3._Components.NavigationLink import NavigationLink as M3NavLink

    class BaseAnchor(UrlMixin, M3Link):
        pass

    class BaseNavLink(UrlMixin, M3NavLink):
        def __init__(self, active=False, **properties):
            super().__init__(selected=active, **properties)

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
