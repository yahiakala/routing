from ._anvil_designer import ArticlesFormTemplate
from anvil import *

from ..routes import Router


class ArticlesForm(ArticlesFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

        data = Router.get_data(self)
        path_params = Router.get_path_params(self)
        search_params = Router.get_search_params(self)
        location = Router.get_location(self)

        self.repeating_panel_1.items = data
