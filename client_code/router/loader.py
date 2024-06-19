import json
from time import sleep
from datetime import datetime
import anvil.server


try:
    from anvil.js.window import Promise
    from anvil.js import await_promise
    from anvil.js import report_exceptions
except ImportError:
    from async_promises import Promise

    def await_promise(promise):
        return promise.get()

    def report_exceptions(fn):
        return fn


in_flight = {}
cache = {}


def clear_cache():
    in_flight.clear()
    cache.clear()


@anvil.server.portable_class
class CachedData:
    def __init__(self, *, data, location):
        self.data = data
        self.location = location
        self.fetched_at = datetime.now()

    def __deserialize__(self, data, gbl_data):
        self.__dict__.update(data, fetched_at=datetime.now())


_inital_request = True


@report_exceptions
def load_data(match, force=False):
    global _inital_request
    is_initial = _inital_request
    _inital_request = False

    route = match.route
    location = match.location
    search_params = match.search_params
    path_params = match.path_params
    deps = match.deps
    key = match.key
    print(key, "data cache key")

    def clean_up_inflight(result=None):
        try:
            del in_flight[key]
            print(key, "deleting in_flight key", repr(key))
        except KeyError as e:
            print(key, "no in_flight key", repr(e))
            pass

        return result

    @report_exceptions
    def load_data_async(resolve, reject):
        from .context import Context

        print(key, "load_data_async")
        sleep(0)  # give control to the event loop
        try:
            data = route.loader(
                location=location,
                search_params=search_params,
                path_params=path_params,
                deps=deps,
            )
            cached = CachedData(data=data, location=location)
            cache[key] = cached
            if Context._current is not None:
                if key == Context._current.match.key:
                    Context._current.data = data

            clean_up_inflight()
            resolve(cached)
        except Exception as e:
            print(repr(e))
            reject(e)

    def create_in_flight_data_promise():
        if key in in_flight:
            print(key, "key already in in_flight")
            return in_flight[key]
        data_promise = Promise(load_data_async)
        in_flight[key] = data_promise

        return data_promise

    if key in cache and not force:
        print("key in cache")
        cached = cache[key]
        fetched_at = cached.fetched_at
        print(
            key,
            "stale time",
            is_initial,
            repr(fetched_at),
            (datetime.now() - fetched_at).total_seconds(),
            route.stale_time,
        )
        if (
            not is_initial
            and (datetime.now() - fetched_at).total_seconds() > route.stale_time
        ):
            print(key, "stale - creating data_promise")
            create_in_flight_data_promise()

    else:
        print(key, "key not in cache")
        cached = await_promise(create_in_flight_data_promise())

    print(key, cached)
    return cached.data


def load_data_promise(match):
    sleep(0)  # give control to the event loop

    @report_exceptions
    def data_promise(resolve, reject):
        try:
            resolve(load_data(match))
        except Exception as e:
            print(repr(e))
            reject(e)

    return Promise(data_promise)
