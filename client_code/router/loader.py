import json
from datetime import datetime
import anvil.server

try:
    from anvil.js.window import Promise
    from anvil.js import await_promise
except ImportError:
    from async_promises import Promise

    def await_promise(promise):
        return promise.get()


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

    @classmethod
    def __deserialize__(cls, data, gbl_data):
        return cls(**data)


def load_data(match):
    route = match.route
    location = match.location
    search_params = match.search_params
    path_params = match.path_params
    path = match.location.path
    deps = route.loader_deps(
        location=location, search_params=search_params, path_params=path_params
    )
    key = f"{path}:{json.dumps(deps, sort_keys=True)}"

    def load_data_async(resolve, reject):
        print("load_data_async")
        try:
            data = route.loader(
                location=location,
                search_params=search_params,
                path_params=path_params,
                deps=deps,
            )
            cached = CachedData(data=data, location=location)
            cache[key] = cached
            print("cached", cached)
            try:
                del in_flight[key]
                print("deleting in_flight key", repr(key))
            except KeyError as e:
                print("no in_flight key", repr(e))
                pass
            resolve(cached)
        except Exception as e:
            print(repr(e))
            reject(e)

    def create_in_flight_data_promise():
        if key in in_flight:
            print("key already in in_flight")
            return in_flight[key]
        data_promise = Promise(load_data_async)
        print("creating data_promise")
        in_flight[key] = data_promise
        return data_promise

    if key in cache:
        print("key in cache")
        cached = cache[key]
        fetched_at = cached.fetched_at
        print(
            "stale time",
            (datetime.now() - fetched_at).total_seconds(),
            route.stale_time,
        )
        if (datetime.now() - fetched_at).total_seconds() > route.stale_time:
            print("stale - creating data_promise")
            create_in_flight_data_promise()

    elif key in in_flight:
        print("key in in_flight")
        cached = await_promise(in_flight[key])

    else:
        print("key not in cache or in_flight")
        cached = await_promise(create_in_flight_data_promise())
        print("cached", cached)

    print(cached)
    return cached.data
