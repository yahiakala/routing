class Deferred:
    def __init__(self):
        pass


def call_async(fn, *args, **kws):
    return fn(*args, **kws)


class Result(list):
    def __init__(self, ok=None, error=None):
        self.ok = ok
        self.error = error
