from time import sleep
from datetime import datetime
from ._non_blocking import call_async
from ._constants import STALE_WHILE_REVALIDATE, NETWORK_FIRST
from ._cached import IN_FLIGHT_DATA, CACHED_DATA
from ._logger import logger
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


@anvil.server.portable_class
class CachedData:
    def __init__(self, *, data, location, mode):
        self.data = data
        self.location = location
        self.mode = mode
        self.fetched_at = datetime.now()

    def __deserialize__(self, data, gbl_data):
        self.__dict__.update(data, fetched_at=datetime.now())


_inital_request = True


# @report_exceptions
def load_data_promise(context, force=False):
    match = context.match
    global _inital_request
    is_initial = _inital_request
    _inital_request = False

    route = match.route
    location = match.location
    search_params = match.search_params
    path_params = match.path_params
    deps = match.deps
    key = match.key
    logger.debug(f"loading data for {key}")

    def clean_up_inflight(result=None):
        try:
            del IN_FLIGHT_DATA[key]
        except KeyError as e:
            pass

        return result

    @report_exceptions
    def on_result(data):
        from ._context import RoutingContext

        logger.debug(f"data loaded: {key}")
        cached = CachedData(data=data, location=location, mode=route.cache_mode)
        CACHED_DATA[key] = cached
        context.data = data

        clean_up_inflight()

    def on_error(error):
        # TODO: handle error
        from ._context import RoutingContext

        logger.debug(f"load error {key}: {error}")
        if RoutingContext._current is not None:
            if key == RoutingContext._current.match.key:
                RoutingContext._current.data = None

    def wrapped_loader(retries=0, **loader_args):
        try:
            result = route.loader(**loader_args)
        except anvil.server.AppOfflineError as e:
            if not retries:
                logger.debug(f"{key} {e!r}, retrying")
                sleep(1)
                result = wrapped_loader(retries=retries + 1, **loader_args)
            elif key in CACHED_DATA:
                logger.debug(f"{key} {e!r} after retrying, using cached data")
                result = CACHED_DATA[key].data
            else:
                raise e
        return result

    def create_in_flight_data_promise():
        if key in IN_FLIGHT_DATA:
            logger.debug(f"{key} data already loading in flight")
            return IN_FLIGHT_DATA[key]

        async_call = call_async(
            wrapped_loader,
            location=location,
            search_params=search_params,
            path_params=path_params,
            deps=deps,
            # router_context=context,
            nav_args=context.nav_args,
        )
        async_call.on_result(on_result)
        async_call.on_error(on_error)

        data_promise = async_call.promise
        IN_FLIGHT_DATA[key] = data_promise

        return data_promise

    if key in CACHED_DATA and not force:
        logger.debug(f"{key} data in cache")
        cached = CACHED_DATA[key]

        fetched_at = cached.fetched_at
        mode = cached.mode

        if is_initial:
            # data came in with startup data
            data_promise = cached.data
        if mode == NETWORK_FIRST:
            logger.debug(f"{key} loading data, {NETWORK_FIRST}")
            data_promise = create_in_flight_data_promise()
        elif mode == STALE_WHILE_REVALIDATE:
            data_promise = cached.data
            is_stale = (datetime.now() - fetched_at).total_seconds() > route.stale_time
            if is_stale:
                logger.debug(
                    f"{key} - reloading in the background, {STALE_WHILE_REVALIDATE}"
                )
                create_in_flight_data_promise()
        else:
            raise Exception("Unknown cache mode")

    else:
        logger.debug(f"{key} data not in cache")
        data_promise = create_in_flight_data_promise()

    return data_promise


def load_data(context, force=False):
    await_promise(load_data_promise(context, force))
    return context.data
