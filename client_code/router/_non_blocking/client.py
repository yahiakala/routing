from anvil.js.window import setTimeout, Function

# We need to make sure the .then method doesn't return a Promise to avoid suspensions
PromiseLike = Function("""
class PromiseLike extends Promise {
    then(...args) {
        Promise.prototype.then.apply(this, args);
    }
}
return PromiseLike;
class Deferred {
    constructor() {
        this.promise = new PromiseLike((resolve, reject) => {
            this.resolve = resolve;
            this.reject = reject;
        });
    }
}
                                 
return [PromiseLike, Deferred];
""")()


class Deferred:
    def __init__(self):
        def callback(resolve, reject):
            self.resolve = resolve
            self.reject = reject

        self.promise = PromiseLike(callback)


# We wrap the result in a obtuse python object to avoid converting python objects to javascript
class Result:
    def __init__(self, ok=None, error=None):
        self.ok = ok
        self.error = error

    def __iter__(self):
        return [self.ok, self.error].__iter__()


def call_async(fn, *args, **kws):
    _deferred = Deferred()

    def call():
        try:
            result = fn(*args, **kws)
            _deferred.resolve(Result(result))
        except Exception as e:
            _deferred.resolve(Result(error=e))

    setTimeout(call, 0)

    return _deferred.promise
