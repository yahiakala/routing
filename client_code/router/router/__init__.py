import anvil

if anvil.is_server_side():
    from .server import create, BlockNavigation

else:
    from .client import create, BlockNavigation
