# SPDX-License-Identifier: MIT
#
# Copyright (c) 2021 The Anvil Extras project team members listed at
# https://github.com/anvilistas/anvil-extras/graphs/contributors
#
# This software is published at https://github.com/anvilistas/anvil-extras

from functools import partial as _partial
import anvil

from anvil.server import call_s as _call_s

from .utils import report_exceptions as _report
from .utils import Promise


if not anvil.is_server_side():
    from anvil.js.window import Function

    # python errors get wrapped when called from a js function in python
    # so instead reject the error from a js function in js

    _deferred = Function(
        "fn",
        """
const deferred = { status: "PENDING", error: null };

deferred.promise = new Promise(async (resolve, reject) => {
    try {
        resolve(await fn());
        deferred.status = "FULFILLED";
    } catch (e) {
        deferred.status = "REJECTED";
        deferred.error = e;
        reject(e);
    }
});

let handledResult = deferred.promise;
let handledError = null;

return Object.assign(deferred, {
    on_result(resultHandler, errorHandler) {
        if (!errorHandler && handledError) {
            // the on_error was already called so provide a dummy handler;
            errorHandler = () => {};
        }
        handledResult = deferred.promise.then(resultHandler, errorHandler);
        handledError = null;
    },
    on_error(errorHandler) {
        handledError = handledResult.catch(errorHandler);
        handledResult = deferred.promise;
    },
    await_result: async () => await deferred.promise,
});
""",
    )

else:

    class Deferred(dict):
        def __init__(self, *args, **kwargs):
            dict.__init__(self, *args, **kwargs)
            self.__dict__ = self

    def _deferred(fn):
        deferred = Deferred(status="PENDING", error=None)

        def callbaack(resolve, reject):
            try:
                resolve(fn())
                deferred.status = "FULFILLED"
            except Exception as e:
                deferred.status = "REJECTED"
                deferred.error = e
                reject(e)

        deferred.promise = Promise(callbaack)

        handlers = {"result": deferred.promise, "error": None}

        def on_result(resultHandler, errorHandler=None):
            if not errorHandler and handlers["error"]:
                # the on_error was already called so provide a dummy handler;
                errorHandler = lambda *args, **kws: None
            handlers["result"] = handlers["result"].then(resultHandler, errorHandler)
            handlers["error"] = None

        def on_error(errorHandler):
            handlers["error"] = handlers["result"].catch(errorHandler)
            handlers["result"] = deferred.promise

        def await_result():
            return deferred.promise.get()

        deferred.update(
            on_result=on_result, on_error=on_error, await_result=await_result
        )

        return deferred


__version__ = "2.6.1"

try:
    # just for a nice repr by default
    _call_s.__name__ = "call_s"
    _call_s.__qualname__ = "anvil.server.call_s"
except AttributeError:
    pass


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
        self._fn = _partial(fn, *args, **kws)
        self._deferred = _deferred(_Result.wrap(self._fn))

    def _check_pending(self):
        if self._deferred.status == "PENDING":
            raise RuntimeError("the async call is still pending")

    @property
    def result(self):
        """If the function call is not complete, raises a RuntimeError
        If the function call is complete:
        Returns: the return value from the function call
        Raises: the error raised by the function call
        """
        self._check_pending()
        return self.await_result()

    @property
    def error(self):
        """Returns the error raised by the function call, else None"""
        self._check_pending()
        return self._deferred.error

    @property
    def status(self):
        """Returns: 'PENDING', 'FULFILLED', 'REJECTED'"""
        return self._deferred.status

    @property
    def promise(self):
        """Returns: JavaScript Promise that resolves to the value from the function call"""
        return Promise(
            lambda resolve, reject: resolve(
                self._deferred.promise.then(lambda r: r.value)
            )
        )

    def on_result(self, result_handler, error_handler=None):
        error_handler = error_handler and _report(error_handler)
        result_handler = _Result.unwrap(_report(result_handler))
        self._deferred.on_result(result_handler, error_handler)
        return self

    def on_error(self, error_handler):
        self._deferred.on_error(_report(error_handler))
        return self

    def await_result(self):
        return self._deferred.await_result().value

    def __repr__(self):
        fn_repr = repr(self._fn).replace("functools.partial", "")
        return f"<non_blocking.AsyncCall{fn_repr}>"


def call_async(fn_or_name, *args, **kws):
    """
    Call a function or a server function (if a string is provided) in a non-blocking way.

    Parameters
    ----------
    fn_or_name: A function or the name of a server function to call.
    """
    if isinstance(fn_or_name, str):
        return _AsyncCall(_call_s, fn_or_name, *args, **kws)
    if callable(fn_or_name):
        return _AsyncCall(fn_or_name, *args, **kws)
    msg = "the first argument must be a callable or the name of a server function"
    raise TypeError(msg)


def wait_for(async_call_object):
    "Wait for a non-blocking function to complete its execution"
    if not isinstance(async_call_object, _AsyncCall):
        raise TypeError(
            f"expected an AsyncCall object, got {type(async_call_object).__name__}"
        )
    return async_call_object.await_result()
