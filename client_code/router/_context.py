from ._invalidate import invalidate
from ._loader import load_data
from ._matcher import Match


class RoutingContext:
    _current = None
    _events = [
        "data_loaded",
        "data_loading",
        "data_error",
        "query_changed",
        "hash_changed",
    ]

    def __init__(self, match: Match, data=None, nav_context=None, form_properties=None):
        self.match = match
        self.deps = match.deps
        self.location = match.location
        self.path = match.path
        self.params = match.params
        self.query = match.query
        self.hash = match.hash
        self.route = match.route
        self.nav_context = nav_context
        self.form_properties = form_properties
        self.error = None
        self._data = data
        self._listeners = {}
        self._blockers = set()

    def _update(self, context):
        self.match = context.match
        self.deps = context.match.deps
        self.nav_context = context.nav_context
        self.form_properties = context.form_properties
        self.location = context.match.location
        self.path = context.match.path
        self.params = context.match.params
        self.query = context.match.query
        self.route = context.match.route
        self.hash = context.match.hash
        # TODO: raise an event if the location has changed

    def _prevent_unload(self):
        for blocker in self._blockers:
            if blocker():
                return True
        return False

    def register_blocker(self, blocker):
        self._blockers.add(blocker)

    def unregister_blocker(self, blocker):
        self._blockers.remove(blocker)

    def _validate_event(self, event):
        if not isinstance(event, str):
            raise TypeError("event must be a string")
        if event not in self._events:
            raise ValueError(f"event {event} not in {self._events}")

    def add_event_handler(self, event, handler):
        self._validate_event(event)
        self._listeners.setdefault(event, []).append(handler)

    def remove_event_handler(self, event, handler):
        self._validate_event(event)
        if event in self._listeners:
            self._listeners[event].remove(handler)

    def _emit(self, event, **kwargs):
        self._validate_event(event)
        kwargs["sender"] = self
        for handler in self._listeners.get(event, []):
            handler(**kwargs)

    def invalidate(self, exact=False):
        # remove ourselves from cached from and cached data
        invalidate(self, exact=exact)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._emit("data_loaded", data=data)

    def _on_data_loaded(self, data):
        self.data = data

    def _on_data_error(self, error):
        self._emit("data_error", error=error)
    
    def reload(self):
        self.invalidate(exact=True)
        if self._current is not self:
            return
        return self._load_data()

    def _load_data(self):
        from ._non_blocking import call_async

        ac = call_async(load_data, self, force=True)
        self._emit("data_loading")
        return ac

    @property
    def _loader_args(self):
        return {
            "location": self.location,
            "path": self.path,
            "query": self.query,
            "params": self.params,
            "deps": self.deps,
            "nav_context": self.nav_context,
            "form_properties": self.form_properties,
        }