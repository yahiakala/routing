from ._BaseLinks import BaseAnchor
from ._LinkCommon import LinkMixinCommon, filter_props, nav_props


class Anchor(BaseAnchor, LinkMixinCommon):
    _anvil_properties_ = [
        *nav_props.values(),
        *filter_props(BaseAnchor._anvil_properties_),
    ]

    def __init__(
        self,
        path=None,
        query=None,
        params=None,
        hash=None,
        nav_context=None,
        **properties,
    ):
        LinkMixinCommon.__init__(
            self,
            path=path,
            query=query,
            params=params,
            hash=hash,
            nav_context=nav_context,
            **properties,
        )
        BaseAnchor.__init__(self, **properties)
