import anvil

if anvil.is_server_side():
    from .server import NavigationBlocker, UnloadBlocker, launch, navigation_emitter

else:
    from .client import NavigationBlocker, UnloadBlocker, launch, navigation_emitter
