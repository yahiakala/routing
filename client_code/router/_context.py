from re import L, T

from ._loader import load_data
from ._matcher import Match


class RoutingContext:
    _current = None
    _events = [
        "data_loaded",
        "data_loading",
        "data_error",
        "search_changed",
        "hash_changed",
    ]

    def __init__(self, match: Match, data=None, nav_args=None):
        self.match = match
        self.location = match.location
        self.path_params = match.path_params
        self.search_params = match.search_params
        self.route = match.route
        self.nav_args = nav_args
        self.error = None
        self._data = data
        self._listeners = {}
        self._blockers = set()

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

    def invalidate(self):
        if self._current is not self:
            # TODO: flag that we need to reload the data for next time
            return

        self._load_data()

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

    def _load_data(self):
        from ._non_blocking import call_async

        async_call = call_async(load_data, self, force=True)
        self._emit("data_loading")
        async_call.on_result(self._on_data_loaded)
        async_call.on_error(self._on_data_error)
