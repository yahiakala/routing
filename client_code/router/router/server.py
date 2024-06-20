def create():
    pass


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
