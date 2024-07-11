from ._LinkCommon import DefaultLink, active_props, nav_props

# This is just temporary to test using other nav links
try:
    from Mantine import utils
    from Mantine.Anchor import Anchor as DefaultLink

    utils.set_color_scheme("light")

except ImportError:
    pass


class NavLink(DefaultLink):
    _anvil_properties_ = [
        *nav_props.values(),
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
        **properties,
    ):
        super().__init__(
            path=path,
            search_params=search_params,
            search=search,
            path_params=path_params,
            hash=hash,
            nav_args=nav_args,
            **properties,
        )
