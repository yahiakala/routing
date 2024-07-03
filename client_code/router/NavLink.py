import anvil
from anvil.js import get_dom_node
from anvil.history import history, Location
from anvil.designer import (
    in_designer,
    get_design_component,
    start_editing_form,
    register_interaction,
)
from ._navigate import nav_args_to_location, navigate_with_location
from ._matcher import get_match
from ._exceptions import InvalidPathParams
from ._segments import Segment
from ._router import navigation_emitter

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
            return self.label

        @text.setter
        def text(self, value):
            self.label = value

except ImportError:
    _DefaultLink = get_design_component(anvil.Link)

    class DefaultLink(_DefaultLink):
        def __init__(self, href=None, **properties):
            self._active = False
            super().__init__(url=href, **properties)

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
            self.role = "selected" if value else None


def wrap_special_method(method_name):
    def wrapper(self, *args, **kwargs):
        method = getattr(self._link, method_name, None)
        if method is not None:
            return method(*args, **kwargs)

    wrapper.__name__ = method_name

    return wrapper


def _temp_hack_to_get_form(self):
    if not in_designer:
        return None

    try:
        from SimpleRoutingExample import routes
    except ImportError:
        pass

    if self._location is None:
        return None
    elif self._location.path is None:
        return None
    match = get_match(location=self._location)

    if match is not None:
        return match.route.form


class NavLink(anvil.Container):
    _anvil_properties_ = [
        {"name": "path", "type": "string", "important": True},
        {"name": "search_params", "type": "object"},
        {"name": "search", "type": "string"},
        {"name": "path_params", "type": "object"},
        {"name": "hash", "type": "string"},
        {"name": "text", "type": "string"},
        {"name": "nav_args", "type": "object"},
        {"name": "active", "type": "boolean"},
        {"name": "exact_path", "type": "boolean"},
        {"name": "exact_search", "type": "boolean"},
        {"name": "exact_hash", "type": "boolean"},
    ]
    _anvil_events_ = [{"name": "click", "defaultEvent": True}]

    def __init__(
        self,
        path="",
        search_params=None,
        search="",
        path_params=None,
        hash="",
        nav_args=None,
        exact_path=False,
        exact_search=False,
        exact_hash=False,
        active=False,
        **properties
    ):
        self._props = dict(
            properties,
            active=active,
            path=path,
            search_params=search_params,
            search=search,
            path_params=path_params,
            hash=hash,
            nav_args=nav_args,
            exact_path=exact_path,
            exact_search=exact_search,
            exact_hash=exact_hash,
        )
        self._location = None
        self._form = None
        self._href = ""
        self._link = DefaultLink(**properties, active=active)
        self.add_event_handler("x-anvil-page-added", self._setup)
        self.add_event_handler("x-anvil-page-removed", self._cleanup)

    def _set_href(self):
        path = self.path
        search = self.search
        path_params = self.path_params
        search_params = self.search_params
        hash = self.hash

        try:
            location = nav_args_to_location(
                path=path,
                path_params=path_params,
                search_params=search_params,
                hash=hash,
            )
        except InvalidPathParams as e:
            if not in_designer:
                raise e
            else:
                location = Location(path=path, search=search, hash=hash)
        if not location.search and search:
            if not search.startswith("?"):
                search = "?" + search
            location.search = search

        self._location = location

        if in_designer:
            self._form = _temp_hack_to_get_form(self)
        elif location.path is not None:
            self._link.href = self._href = location.get_url(False)

    @property
    def nav_args(self):
        return self._props.get("nav_args")

    @nav_args.setter
    def nav_args(self, value):
        self._props["nav_args"] = value

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

    def _on_navigate(self, **nav_args):
        curr_location = history.location
        location = self._location
        active = True

        if location is None:
            active = False
        elif self.exact_path and curr_location.path != location.path:
            active = False
        elif self.exact_search and curr_location.search != location.search:
            active = False
        elif self.exact_hash and curr_location.hash != location.hash:
            active = False
        elif curr_location.path != location.path:
            # check if the current location is a parent of the new location
            curr_segments = Segment.from_path(curr_location.path)
            location_segments = Segment.from_path(location.path)
            if len(location_segments) > len(curr_segments):
                active = False
            else:
                for gbl, loc in zip(curr_segments, location_segments):
                    if gbl.value == loc.value or loc.is_param():
                        continue
                    active = False
                    break

        self.active = active

    def _do_click(self, e):
        if not in_designer:
            navigate_with_location(self._location, nav_args=self.nav_args)
        elif self._form is not None:
            start_editing_form(self, self._form)

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
        self._set_href()
        if in_designer:
            if self._form is not None:
                register_interaction(self, self._el, "dblclick", self._do_click)
        else:
            navigation_emitter.subscribe(self._on_navigate)

    def _cleanup(self, **event_args):
        self._link.raise_event("x-anvil-page-removed", **event_args)
        el = self._el
        if el is None:
            return
        self._el = None
        el.removeEventListener("click", self._on_click, True)
        navigation_emitter.unsubscribe(self._on_navigate)

    _anvil_setup_dom_ = wrap_special_method("_anvil_setup_dom_")

    @property
    def _anvil_dom_element_(self):
        return self._link._anvil_dom_element_

    _anvil_get_container_design_info_ = wrap_special_method(
        "_anvil_get_container_design_info_"
    )
    _anvil_enable_drop_mode_ = wrap_special_method("_anvil_enable_drop_mode_")
    _anvil_disable_drop_mode_ = wrap_special_method("_anvil_disable_drop_mode_")
