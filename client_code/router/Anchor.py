from ._LinkCommon import DefaultLink, LinkMixinCommon, filter_props, nav_props

# This is just temporary to test using other nav links
try:
    from Mantine import utils
    from Mantine.Anchor import Anchor as DefaultLink

    utils.set_color_scheme("light")

except ImportError:
    pass


class Anchor(DefaultLink, LinkMixinCommon):
    _anvil_properties_ = [
        *nav_props.values(),
        *filter_props(DefaultLink._anvil_properties_),
    ]

    def __init__(
        self,
        path="",
        query=None,
        search="",
        params=None,
        hash="",
        nav_args=None,
        **properties,
    ):
        LinkMixinCommon.__init__(
            self,
            path=path,
            query=query,
            search=search,
            params=params,
            hash=hash,
            nav_args=nav_args,
            **properties,
        )
        DefaultLink.__init__(self, **properties)
