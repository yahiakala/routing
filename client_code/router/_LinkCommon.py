import anvil
from anvil import Component
from anvil.designer import (
    get_design_component,
    in_designer,
    register_interaction,
    start_editing_form,
)
from anvil.history import Location
from anvil.js import get_dom_node

from ._exceptions import InvalidPathParams
from ._logger import logger
from ._matcher import get_match
from ._navigate import nav_args_to_location, navigate_with_location
from ._router import navigation_emitter
from ._utils import ensure_dict

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
        self.role = "selected" if value else None


def _temp_hack_to_get_form(self):
    if not in_designer:
        return None

    try:
        from SimpleRoutingExample import routes  # noqa: F401
    except (ImportError, ModuleNotFoundError, AttributeError):
        pass

    if self._location is None:
        return None
    elif self._location.path is None:
        return None
    match = get_match(location=self._location)

    if match is not None:
        return match.route.form


nav_props = {
    "path": {
        "name": "path",
        "type": "string",
        "group": "navigation",
        "priority": 100,
        "important": True,
    },
    "query": {"name": "query", "type": "object", "group": "navigation"},
    "params": {"name": "params", "type": "object", "group": "navigation"},
    "hash": {"name": "hash", "type": "string", "group": "navigation"},
    "nav_context": {"name": "nav_context", "type": "object", "group": "navigation"},
    "form_properties": {
        "name": "form_properties",
        "type": "object",
        "group": "navigation",
    },
}

active_props = {
    "active": {"name": "active", "type": "boolean", "important": True},
    "exact_path": {"name": "exact_path", "type": "boolean", "group": "active"},
    "exact_query": {"name": "exact_query", "type": "boolean", "group": "active"},
    "exact_hash": {"name": "exact_hash", "type": "boolean", "group": "active"},
}

all_props = {**nav_props, **active_props}

ignore_props = ["href", *all_props]


def filter_props(prop_list):
    return filter(lambda prop: prop["name"] not in ignore_props, prop_list)


class LinkMixinCommon(Component):
    def __init__(self, **properties):
        self._props = properties
        self._location = None
        self._form = None
        self._invalid = None
        self.add_event_handler("x-anvil-page-added", self._setup)
        self.add_event_handler("x-anvil-page-removed", self._cleanup)
        self.add_event_handler("click", self._on_click)

    def _do_click(self, e):
        if not in_designer:
            if self._location is not None:
                logger.debug(f"NavLink clicked, navigating to {self._location}")
                navigate_with_location(
                    self._location,
                    nav_context=self.nav_context,
                    form_properties=self.form_properties,
                )
            elif self._invalid is not None:
                raise self._invalid
            else:
                logger.debug("NavLink clicked, but with invalid path, query or hash")
        elif self._form is not None:
            start_editing_form(self, self._form)

    def _on_click(self, **event_args):
        event = event_args.get("event")
        if event is None:
            raise RuntimeError("Link provider did not pass the event")
        if event.ctrlKey or event.metaKey or event.shiftKey:
            logger.debug(
                "NavLink clicked, but with modifier keys - letting browser handle"
            )
            return
        event.preventDefault()
        self._do_click(event)

    def _setup(self, **event_args):
        # we have to do this when we're on the page in case links are relative
        self._set_href()

        if in_designer and self._form is not None:
            register_interaction(self, get_dom_node(self), "dblclick", self._do_click)

        if not in_designer:
            navigation_emitter.add_event_handler("navigate", self._set_href)

    def _cleanup(self, **event_args):
        navigation_emitter.remove_event_handler("navigate", self._set_href)

    @property
    def nav_context(self):
        return self._props.get("nav_context")

    @nav_context.setter
    def nav_context(self, value):
        value = ensure_dict(value, "nav_context")
        self._props["nav_context"] = value

    @property
    def form_properties(self):
        return self._props.get("form_properties")

    @form_properties.setter
    def form_properties(self, value):
        value = ensure_dict(value, "form_properties")
        self._props["form_properties"] = value

    @property
    def path(self):
        return self._props.get("path")

    @path.setter
    def path(self, value):
        self._props["path"] = value
        self._set_href()

    @property
    def query(self):
        return self._props.get("query")

    @query.setter
    def query(self, value):
        self._props["query"] = value
        self._set_href()

    @property
    def params(self):
        return self._props.get("params")

    @params.setter
    def params(self, value):
        self._props["params"] = value
        self._set_href()

    @property
    def hash(self):
        return self._props.get("hash")

    @hash.setter
    def hash(self, value):
        self._props["hash"] = value
        self._set_href()

    @property
    def exact_path(self):
        return self._props.get("exact_path")

    @exact_path.setter
    def exact_path(self, value):
        self._props["exact_path"] = value

    @property
    def exact_query(self):
        return self._props.get("exact_query")

    @exact_query.setter
    def exact_query(self, value):
        self._props["exact_query"] = value

    @property
    def exact_hash(self):
        return self._props.get("exact_hash")

    @exact_hash.setter
    def exact_hash(self, value):
        self._props["exact_hash"] = value

    def _set_href(self, **nav_args):
        prev_location = self._location

        path = self.path or None
        params = self.params
        query = self.query
        hash = self.hash

        # fast path
        if (
            path is not None
            and not callable(query)
            and not in_designer
            and prev_location is not None
        ):
            return

        self._location = None
        self._form = None

        try:
            location = nav_args_to_location(
                path=path,
                params=params,
                query=query,
                hash=hash,
            )
        except InvalidPathParams as e:
            if not in_designer:
                self._invalid = e
                self.href = ""
                return
            else:
                location = Location(path=path, hash=hash)
        else:
            self._invalid = None

        self._location = location

        if prev_location == location:
            return

        if in_designer:
            self._form = _temp_hack_to_get_form(self)
        elif location.path is not None:
            self.href = location.get_url(True)
