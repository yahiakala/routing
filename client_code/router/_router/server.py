def launch():
    raise NotImplementedError("launch is not implemented on the server")


class _Blocker:
    def block(self):
        pass

    def unblock(self):
        pass


class NavigationBlocker(_Blocker):
    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass


class UnloadBlocker(_Blocker):
    pass


class _NavigationEmitter:
    def subscribe(self, fn):
        pass

    def unsubscribe(self, fn):
        pass

    def emit(self, *args, **kwargs):
        pass


navigation_emitter = _NavigationEmitter()
