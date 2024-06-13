from ._anvil_designer import ArticlesFormTemplate
from anvil import *


class ArticlesForm(ArticlesFormTemplate):
    def __init__(self, data=None, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.repeating_panel_1.items = data or []
