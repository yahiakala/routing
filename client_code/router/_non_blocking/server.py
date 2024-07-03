class Deferred:
    def __init__(self):
        pass


def call_async(fn, *args, **kws):
    print("call_async", fn, args, kws)
    return fn(*args, **kws)
