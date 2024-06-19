from re import T

from .loader import load_data
from .matcher import Match
from ._deferred import call_async


class Context:
    _current = None
    _events = [
        "data_loaded",
        "data_loading",
        "data_error",
        "search_changed",
        "hash_changed",
    ]

    def __init__(self, match: Match, data=None):
        self.match = match
        self.location = match.location
        self.path_params = match.path_params
        self.search_params = match.search_params
        self.route = match.route
        self.data = data
        self._listeners = {}

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

    def _on_data_loaded(self, data):
        self.data = data
        self._emit("data_loaded", data=data)
    
    def _on_data_error(self, error):
        self._emit("data_error", error=error)

    def _load_data(self):
        async_call = call_async(load_data, self.match)
        self._emit("data_loading")
        async_call.on_result(self._on_data_loaded)
        async_call.on_error(self._on_data_error)
