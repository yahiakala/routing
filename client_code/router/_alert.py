# Copyright (c) 2024 Anvil
# SPDX-License-Identifier: MIT

import anvil
from anvil import alert as anvil_alert
from anvil import confirm as anvil_confirm

from ._router import NavigationBlocker, navigation_emitter

__version__ = "0.3.0"

dismissible_alerts = []


def _on_navigate(**kws):
    global dismissible_alerts
    for alert in dismissible_alerts:
        alert.content.raise_event("x-close-alert")


navigation_emitter.add_event_handler("navigate", _on_navigate)


class DismissibleAlert:
    def __init__(self, content):
        self.content = content

    def __enter__(self):
        dismissible_alerts.append(self)

    def __exit__(self, *args):
        global dismissible_alerts
        dismissible_alerts = [x for x in dismissible_alerts if x is not self]


def wrap_alert(alert_method):
    def alert(content, *args, dismissible=True, **kwargs):
        if isinstance(content, str):
            content = anvil.Label(text=content)

        if not dismissible:
            with DismissibleAlert(content):
                return alert_method(content, *args, dismissible=dismissible, **kwargs)
        else:
            with NavigationBlocker():
                return alert_method(content, *args, dismissible=dismissible, **kwargs)

    return alert


alert = wrap_alert(anvil_alert)
confirm = wrap_alert(anvil_confirm)
