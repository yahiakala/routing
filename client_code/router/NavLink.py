import anvil
from anvil.js import get_dom_node
from ._navigate import navigate
from anvil.history import history
from anvil.designer import in_designer, get_design_component

try:
    from Mantine.NavLink import NavLink as MantineNavLink
    from Mantine import utils

    utils.set_color_scheme("light")

    class DefaultLink(MantineNavLink):
        def __init__(self, text=None, **properties):
            super().__init__(label=text, **properties)

        @property
        def text(self):
            print("GET TEXT", self.label)
            return self.label

        @text.setter
        def text(self, value):
            print("SET TEXT", value)
            self.label = value

except ImportError:
    _DefaultLink = get_design_component(anvil.Link)

    class DefaultLink(_DefaultLink):
        def __init__(self, href=None, **properties):
            super().__init__(url=href, **properties)

        @property
        def href(self):
            return self.url

        @href.setter
        def href(self, value):
            self.url = value


def wrap_special_method(method_name):
    def wrapper(self, *args, **kwargs):
        method = getattr(self._link, method_name, None)
        if method is not None:
            return method(*args, **kwargs)

    wrapper.__name__ = method_name

    return wrapper


class NavLink(anvil.Container):
    _anvil_properties_ = [
        {"name": "href", "type": "string"},
        {"name": "text", "type": "string"},
    ]
    _anvil_events_ = [{"name": "click", "defaultEvent": True}]

    def __init__(self, **properties):
        self._props = properties
        self._link = DefaultLink(**properties)
        self.href = self.href
        self.add_event_handler("x-anvil-page-added", self._setup)
        self.add_event_handler("x-anvil-page-removed", self._cleanup)
    
    # def raise_event(self, event_name, **event_args):
    #     super().raise_event(event_name, **event_args)
    #     if event_name != "click":
    #         self._link.raise_event(event_name, **event_args)

    def get_components(self):
        return self._link.get_components()

    def add_component(self, component, **properties):
        self._link.add_component(component, **properties)

    def clear(self):
        self._link.clear()

    @property
    def href(self):
        return self._props.get("href")

    @href.setter
    def href(self, value):
        self._props["href"] = value
        if not in_designer:
            self._link.href = history.createHref(value)

    @property
    def text(self):
        return self._props.get("text")

    @text.setter
    def text(self, value):
        self._props["text"] = value
        self._link.text = value

    def _on_click(self, e):
        if e.ctrlKey or e.metaKey or e.shiftKey:
            return
        e.preventDefault()
        e.stopImmediatePropagation()

        href = self.href
        history.push(href)

    def _setup(self, **event_args):
        self._link.raise_event("x-anvil-page-added", **event_args)
        print("SETUP")
        self._el = get_dom_node(self._link)
        self._el.addEventListener("click", self._on_click, True)

    def _cleanup(self, **event_args):
        self._link.raise_event("x-anvil-page-removed", **event_args)
        print("CLEANUP")
        el = self._el
        if el is None:
            return
        self._el = None
        el.removeEventListener("click", self._on_click, True)

    _anvil_setup_dom_ = wrap_special_method("_anvil_setup_dom_")

    @property
    def _anvil_dom_element_(self):
        return self._link._anvil_dom_element_

    _anvil_get_container_design_info_ = wrap_special_method(
        "_anvil_get_container_design_info_"
    )
    _anvil_enable_drop_mode_ = wrap_special_method("_anvil_enable_drop_mode_")
    _anvil_disable_drop_mode_ = wrap_special_method("_anvil_disable_drop_mode_")
