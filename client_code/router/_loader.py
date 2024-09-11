from datetime import datetime, timedelta
from time import sleep

import anvil.server

from ._cached import CACHED_DATA, IN_FLIGHT_DATA
from ._constants import CACHE_FIRST, NETWORK_FIRST, NO_CACHE, STALE_WHILE_REVALIDATE
from ._logger import logger
from ._matcher import get_match
from ._navigate import get_nav_location
from ._non_blocking import Result, call_async
from ._utils import await_promise, report_exceptions


@anvil.server.portable_class
class CachedData:
    def __init__(self, *, data, location, mode, gc_time):
        self.data = data
        self.location = location
        self.mode = mode
        self.gc_time = gc_time
        self.fetched_at = datetime.now()

    def _should_gc(self):
        return datetime.now() - self.fetched_at > timedelta(seconds=self.gc_time)

    def __deserialize__(self, data, gbl_data):
        self.__dict__.update(data, fetched_at=datetime.now())

    def __repr__(self):
        return f"<CachedData {self.location} data={self.data!r}>"


_initial_request = True


def load_data_promise(context, force=False):
    match = context.match
    global _initial_request
    is_initial = _initial_request
    _initial_request = False

    route = match.route
    location = match.location
    key = match.key
    logger.debug(f"loading data for {key}")

    def clean_up_inflight():
        try:
            del IN_FLIGHT_DATA[key]
        except KeyError:
            pass

    @report_exceptions
    def on_result(result):
        data, error = result
        clean_up_inflight()

        if error is not None:
            logger.debug(f"data load error: {error}")
            # TODO: is this the right thing to do?
            context.set_data(None, error)
            return
        else:
            logger.debug(f"data loaded: {key}")
            mode = route.cache_data_mode
            gc_time = route.gc_time
            if mode != NO_CACHE:
                cached = CachedData(
                    data=data, location=location, mode=mode, gc_time=gc_time
                )
                CACHED_DATA[key] = cached
            context.set_data(data)

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

        data_promise = call_async(wrapped_loader, **context._loader_args)
        data_promise.then(on_result)
        IN_FLIGHT_DATA[key] = data_promise

        return data_promise

    if key in CACHED_DATA and not force:
        logger.debug(f"{key} data in cache")
        cached = CACHED_DATA[key]

        fetched_at = cached.fetched_at
        mode = cached.mode

        if is_initial:
            logger.debug("initial request, using cache")
            # data came in with startup data
            data_promise = Result(cached.data)
            if cached.mode == NO_CACHE:
                # we were loaded from server data - remove from the cache now
                del CACHED_DATA[key]
        elif mode == CACHE_FIRST:
            logger.debug(f"{key} loading data, {CACHE_FIRST}")
            data_promise = Result(cached.data)
        elif mode == NETWORK_FIRST:
            logger.debug(f"{key} loading data, {NETWORK_FIRST}")
            data_promise = create_in_flight_data_promise()
        elif mode == STALE_WHILE_REVALIDATE:
            data_promise = Result(cached.data)
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


def use_data(
    context_or_path_or_url=None,
    *,
    path=None,
    params=None,
    query=None,
    hash=None,
):
    from ._context import RoutingContext

    location = get_nav_location(
        context_or_path_or_url, path=path, query=query, params=params, hash=hash
    )
    match = get_match(location)
    if match is None:
        raise Exception(f"No match {location}")

    key = match.key

    if key in CACHED_DATA:
        logger.debug(f"using cached data for {key}")
        data_promise = Result(CACHED_DATA[key].data)
    elif key in IN_FLIGHT_DATA:
        logger.debug(f"using in flight data for {key}")
        data_promise = IN_FLIGHT_DATA[key]
    else:
        logger.debug(f"loading data for {key}")
        context = RoutingContext(match=match)
        data_promise = load_data_promise(context)

    data, error = await_promise(data_promise)
    if error is not None:
        raise error
    return data
