import anvil

if anvil.is_server_side():
    from .server import create, NavigationBlocker, UnloadBlocker

else:
    from .client import create, NavigationBlocker, UnloadBlocker
