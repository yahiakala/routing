import anvil
from anvil.js import get_dom_node
from ._navigate import navigate
from anvil.history import history

def default_link(href, **properties):
    link_component = anvil.Link(source=href)
    return link_component


class NavLink(anvil.Component):
    _anvil_properties_ = [{"name": "href", "type": "string"}]
    _anvil_events_ = [{"name": "click", "defaultEvent": True}]

    def __init__(self, **properties):
        self.href = properties.get("href")
        self._link = default_link(href=self.href)
        self._link.add_event_handler("x-anvil-page-added", self._setup)
        self._link.add_event_handler("x-anvil-page-removed", self._cleanup)

    
    def _on_click(self, e):
        if e.ctrlKey or e.metaKey or e.shiftKey:
            return
        e.preventDefault()
        e.stopImmediatePropagation()

        href = self.href
        navigate(path=href)
    
    def _setup(self):
        self._el = get_dom_node(self._link)
        self._el.addEventListener("click", self._on_click, True)
    
    def _cleanup(self):
        el = self._el
        if el is None:
            return
        self._el = None
        el.removeEventListener("click", self._on_click, True)
        
    def _anvil_setup_dom_(self):
        return self._link._anvil_setup_dom_()
    
    @property
    def _anvil_dom_element_(self):
        return self._link._anvil_dom_element_
        

