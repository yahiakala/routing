import anvil


if anvil.is_server_side():
    from .server import Deferred
else:
    from .client import Deferred, call_async
