from ._anvil_designer import PendingFormTemplate
from anvil import *
import anvil.server


class PendingForm(PendingFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.loading = anvil.server.loading_indicator(self.spacer_1)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.loading.start()

    def form_hide(self, **event_args):
        """This method is called when the form is removed from the page"""
        self.loading.stop()

    
