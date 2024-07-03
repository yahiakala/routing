CACHED_FORMS = {}
CACHED_DATA = {}
IN_FLIGHT_DATA = {}


def clear_cache():
    CACHED_FORMS.clear()
    CACHED_DATA.clear()
    IN_FLIGHT_DATA.clear()
