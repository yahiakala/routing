import anvil


if anvil.is_server_side():
    from .server import Deferred, call_async
else:
    from .client import Deferred, call_async
