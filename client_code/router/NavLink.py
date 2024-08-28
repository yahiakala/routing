from anvil.designer import in_designer

from ._context import RoutingContext
from ._LinkCommon import (
    DefaultLink,
    LinkMixinCommon,
    active_props,
    filter_props,
    nav_props,
)
from ._router import navigation_emitter
from ._segments import Segment

# This is just temporary to test using other nav links
try:
    from Mantine import utils
    from Mantine.NavLink import NavLink as DefaultLink

    utils.set_color_scheme("light")

except ImportError:
    pass


class NavLink(DefaultLink, LinkMixinCommon):
    _anvil_properties_ = [
        *nav_props.values(),
        *active_props.values(),
        *filter_props(DefaultLink._anvil_properties_),
    ]

    def __init__(
        self,
        path="",
        query=None,
        params=None,
        hash="",
        nav_context=None,
        exact_path=False,
        exact_query=False,
        exact_hash=False,
        **properties,
    ):
        LinkMixinCommon.__init__(
            self,
            path=path,
            query=query,
            params=params,
            hash=hash,
            nav_context=nav_context,
            exact_path=exact_path,
            exact_query=exact_query,
            exact_hash=exact_hash,
            **properties,
        )
        DefaultLink.__init__(self, **properties)

        if not in_designer:
            self.add_event_handler(
                "x-anvil-page-added",
                lambda **e: navigation_emitter.subscribe(self._on_navigate),
            )
            self.add_event_handler(
                "x-anvil-page-removed",
                lambda **e: navigation_emitter.unsubscribe(self._on_navigate),
            )

    def _on_navigate(self, **nav_args):
        curr_context: RoutingContext = RoutingContext._current
        location = self._location
        active = True

        if location is None:
            active = False
        elif self.exact_path and curr_context.path != location.path:
            active = False
        elif self.exact_query and curr_context.query != self.query:
            active = False
        elif self.exact_hash and curr_context.hash != location.hash:
            active = False
        elif curr_context.path != location.path:
            # check if the current location is a parent of the new location
            curr_segments = Segment.from_path(curr_context.path)
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
