import anvil
from anvil.js import get_dom_node
from ._navigate import navigate
from anvil.history import history
from anvil.designer import (
    in_designer,
    get_design_component,
    start_editing_form,
    register_interaction,
)
from ._navigate import nav_args_to_location
from ._matcher import get_match

# This is just temporary to test using other nav links
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
        {"name": "path", "type": "string", "important": True},
        {"name": "search_params", "type": "object"},
        {"name": "search", "type": "string"},
        {"name": "path_params", "type": "object"},
        {"name": "hash", "type": "string"},
        {"name": "text", "type": "string"},
    ]
    _anvil_events_ = [{"name": "click", "defaultEvent": True}]

    def __init__(
        self,
        path=None,
        search_params=None,
        search=None,
        path_params=None,
        hash="",
        **properties
    ):
        self._props = dict(
            properties,
            path=path,
            search_params=search_params,
            search=search,
            path_params=path_params,
            hash=hash,
        )
        self._location = None
        self._href = ""
        self._link = DefaultLink(**properties)
        self._set_href()
        self.add_event_handler("x-anvil-page-added", self._setup)
        self.add_event_handler("x-anvil-page-removed", self._cleanup)

    def _set_href(self):
        path = self.path
        search = self.search
        path_params = self.path_params
        search_params = self.search_params
        hash = self.hash

        location = nav_args_to_location(path, path_params, search_params, hash)
        if not location.search and search:
            if not search.startswith("?"):
                search = "?" + search
            location.search = search
        self._location = location

        if in_designer:
            return
        self._link.href = self._href = history.createHref(location)

    @property
    def path(self):
        return self._props.get("path")

    @path.setter
    def path(self, value):
        self._props["path"] = value
        self._set_href()

    @property
    def search_params(self):
        return self._props.get("search_params")

    @search_params.setter
    def search_params(self, value):
        self._props["search_params"] = value
        self._set_href()

    @property
    def search(self):
        return self._props.get("search")

    @search.setter
    def search(self, value):
        self._props["search"] = value
        self._set_href()

    @property
    def path_params(self):
        return self._props.get("path_params")

    @path_params.setter
    def path_params(self, value):
        self._props["path_params"] = value
        self._set_href()

    @property
    def hash(self):
        return self._props.get("hash")

    @hash.setter
    def hash(self, value):
        self._props["hash"] = value
        self._set_href()

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
    def text(self):
        return self._props.get("text")

    @text.setter
    def text(self, value):
        self._props["text"] = value
        self._link.text = value

    def _do_click(self, e):
        href = self._href
        if not in_designer:
            history.push(href)
        else:
            from SimpleRoutingExample import routes
            from ._route import sorted_routes

            print(self._location)
            match = get_match(location=self._location)
            print(match)
            if match is not None:
                start_editing_form(match.route.form)

    def _on_click(self, e):
        if e.ctrlKey or e.metaKey or e.shiftKey:
            return
        e.preventDefault()
        e.stopImmediatePropagation()
        self._do_click(e)

    def _setup(self, **event_args):
        self._link.raise_event("x-anvil-page-added", **event_args)
        self._el = get_dom_node(self._link)
        self._el.addEventListener("click", self._on_click, True)
        if in_designer:
            register_interaction(self, self._el, "dblclick", self._do_click)

    def _cleanup(self, **event_args):
        self._link.raise_event("x-anvil-page-removed", **event_args)
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
