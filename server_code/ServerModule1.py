import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
@anvil.server.callable
def load_articles():
  return [{"id": 0, "name": "foo"}, {"id": 1, "name": "bar"}]

# from . import routes
# from .router import router

# router.create()