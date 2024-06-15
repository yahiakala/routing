from re import T
from .matcher import Match


class Context:
    _events = ["data_loaded", "data_error", "search_changed", "hash_changed"]

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
        # TODO: reload the data and emit the data_loaded event
        pass


