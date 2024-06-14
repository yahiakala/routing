try:
    from async_promises import Promise
except ImportError:

    class Promise:
        def __init__(self, fn):
            self.fn = fn
            self.result = None
            self.error = None
            self.resolved = False

        def get(self):
            if self.resolved:
                return self.result

            self.fn(self.resolve, self.reject)
            if self.error:
                raise self.error
            return self.result

        def resolve(self, result):
            self.result = result
            self.resolved = True

        def reject(self, error):
            self.error = error
            self.resolved = True

        @classmethod
        def race(cls, promises):
            raise NotImplementedError


def await_promise(promise):
    return promise.get()


def report_exceptions(fn):
    return fn


def setTimeout(ms=0):
    return None

