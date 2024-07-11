from anvil.designer import in_designer
from anvil.history import history
from ._segments import Segment
from ._router import navigation_emitter
from ._LinkCommon import DefaultLink, LinkMixinCommon, active_props, nav_props

# This is just temporary to test using other nav links
try:
    from Mantine import utils
    from Mantine.NavLink import NavLink as DefaultLink

    utils.set_color_scheme("light")

except ImportError:
    pass


class NavLink(LinkMixinCommon, DefaultLink):
    _anvil_properties_ = [
        *nav_props.values(),
        *active_props.values(),
        *DefaultLink._anvil_properties_,
    ]

    def __init__(
        self,
        path="",
        search_params=None,
        search="",
        path_params=None,
        hash="",
        nav_args=None,
        exact_path=False,
        exact_search=False,
        exact_hash=False,
        **properties,
    ):
        super().__init__(
            path=path,
            search_params=search_params,
            search=search,
            path_params=path_params,
            hash=hash,
            nav_args=nav_args,
            exact_path=exact_path,
            exact_search=exact_search,
            exact_hash=exact_hash,
            **properties,
        )
        if not in_designer:
            self.add_event_handler("x-anvil-page-added", lambda **e: navigation_emitter.subscribe(self._on_navigate))
            self.add_event_handler("x-anvil-page-removed", lambda **e: navigation_emitter.unsubscribe(self._on_navigate))


    def _on_navigate(self, **nav_args):
        curr_location = history.location
        location = self._location
        active = True

        if location is None:
            active = False
        elif self.exact_path and curr_location.path != location.path:
            active = False
        elif self.exact_search and curr_location.search != location.search:
            active = False
        elif self.exact_hash and curr_location.hash != location.hash:
            active = False
        elif curr_location.path != location.path:
            # check if the current location is a parent of the new location
            curr_segments = Segment.from_path(curr_location.path)
            location_segments = Segment.from_path(location.path)
            if len(location_segments) > len(curr_segments):
                active = False
            else:
                for gbl, loc in zip(curr_segments, location_segments):
                    if gbl.value == loc.value or loc.is_param():
                        continue
                    active = False
                    break

        self.active = active