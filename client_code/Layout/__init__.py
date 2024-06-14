from ._anvil_designer import LayoutTemplate
from anvil import *
from ..router.navigate import navigate



class Layout(LayoutTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        navigate("/")

    def button_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        navigate("/articles")

