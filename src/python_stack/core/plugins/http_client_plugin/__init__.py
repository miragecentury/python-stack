"""
Plugin to manage the http client.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from inject import Binder

if TYPE_CHECKING:
    from python_stack.core.application import AbstractApplication


# pylint: disable=unused-argument
def load(application: "AbstractApplication") -> Callable[[Binder], None] | None:
    """
    Load the http_client plugin.

    This method is called when the plugin is loaded.
    """

    return None


def on_startup() -> None:
    """
    Execute code when the application starts.

    This method is called when the application starts.
    """
    pass


def on_shutdown() -> None:
    """
    Execute code when the application stops.

    This method is called when the application stops.
    """
    pass
