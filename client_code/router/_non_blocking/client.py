import re
from anvil.js.window import Function, Promise
from anvil.js import report_exceptions as _report
from functools import partial


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


# class PromiseLike(dict):
#     def __init__(self, promise):
#         dict.__init__(
#             self,
#             {
#                 "then": self._then,
#                 "catch": promise["catch"],
#                 "finally": promise["finally"],
#             },
#         )
#         self._promise = promise
#         self.__dict__ = self

#     def _then(self, on_fulfilled, on_rejected=None):
#         result = self._promise.then(on_fulfilled, on_rejected)
#         if isinstance(result, _Result):
#             return result.value
#         return result


class _Result:
    # dicts may come back as javascript object literals
    # so wrap the results in a more opaque python object
    def __init__(self, value):
        self.value = value

    @staticmethod
    def wrap(fn):
        def wrapper():
            return _Result(fn())

        return wrapper

    @staticmethod
    def unwrap(fn):
        def unwrapper(res):
            return fn(res.value)

        return unwrapper


class _AsyncCall:
    def __init__(self, fn, *args, **kws):
        self._fn = partial(fn, *args, **kws)
        self._async_call = _JsAsyncCall(_Result.wrap(self._fn))

    def _check_pending(self):
        if self._async_call.status == "PENDING":
            raise RuntimeError("the async call is still pending")

    @property
    def promise(self):
        def promise_handler(resolve, reject):
            return self._async_call.promise.then(_Result.unwrap(resolve), reject)

        return Promise(promise_handler)

    def on_result(self, result_handler, error_handler=None):
        error_handler = error_handler and _report(error_handler)
        result_handler = _Result.unwrap(_report(result_handler))
        self._async_call.on_result(result_handler, error_handler)
        return self

    def on_error(self, error_handler):
        self._async_call.on_error(_report(error_handler))
        return self

    def await_result(self):
        return self._async_call.await_result().value

    def __repr__(self):
        fn_repr = repr(self._fn).replace("functools.partial", "")
        return f"<AsyncCall{fn_repr}>"


def call_async(fn, *args, **kws):
    return _AsyncCall(fn, *args, **kws)
