from ._anvil_designer import ArticlesFormTemplate
from anvil import *

from ..routes import ArticlesRoute


class ArticlesForm(ArticlesFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.repeating_panel_1.items = ArticlesRoute.data


        # Any code you write here will run before the form opens.
