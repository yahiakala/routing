from functools import partial, wraps

from anvil.js import report_exceptions as _report
from anvil.js.window import Function, Promise

_JS_Objects = """
class Deferred {
    constructor() {
        this.promise = new Promise(async (resolve, reject) => {
            this.resolve = resolve;
            this.reject = reject;
        });
    }
}


class AsyncCall {
    constructor(fn) {
        this.status = "PENDING";
        this.error = null;
        this.deferred = new Deferred();
        this.promise = this.deferred.promise;
        const async_call = async () => {
            try {
                const result = await fn();
                this.deferred.resolve(result);
                this.status = "FULFILLED";
                this.result = result;
            } catch (e) {
                this.status = "REJECTED";
                this.error = e;
                this.deferred.reject(e);
            }
        }
        async_call();
        this._resultHandler = this.promise;
        this._errorHandler = null;
    }
    on_result(resultHandler, errorHandler) {
        if (!errorHandler && this._errorHandler) {
            // the on_error was already called so provide a dummy handler;
            errorHandler = () => {};
        }
        this._resultHandler = this.promise.then(resultHandler, errorHandler);
        return this;
    }
    on_error(errorHandler) {
        this._errorHandler = this._resultHandler.catch(errorHandler);
        this._resultHandler = this.promise;
    }
    async await_result() {
        return await this.promise;
    }
}

return [Deferred, AsyncCall];

"""


Deferred, _JsAsyncCall = Function(_JS_Objects)()

class Result:
    def __init__(self, ok=None, error=None):
        self.ok = ok
        self.error = error
    
    def __iter__(self):
        return [self.ok, self.error].__iter__()
    

def wrap_result(fn):

    @wraps(fn)
    def wrapper(*args, **kws):
        try:
            result = fn(*args, **kws)
        except Exception as e:
            return Result(error=e)
        return wrap_result(result)

    return wrapper

class _AsyncCall:
    def __init__(self, fn, *args, **kws):
        self._fn = partial(fn, *args, **kws)
        self._async_call = _JsAsyncCall(wrap_result(self._fn))

    @property
    def promise(self):
        return self._async_call.promise

    def on_result(self, result_handler):
        self._async_call.on_result(result_handler)
        return self

    def await_result(self):
        return self._async_call.await_result()

    def __repr__(self):
        fn_repr = repr(self._fn).replace("functools.partial", "")
        return f"<AsyncCall{fn_repr}>"


def call_async(fn, *args, **kws):
    return _AsyncCall(fn, *args, **kws)
