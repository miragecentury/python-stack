"""
This module is the entry point for the logging plugin.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from inject import Binder

from python_stack.core.application.abstracts.plugins import PluginPriorityEnum
from python_stack.core.application.enums import Environment

from .configures import configure_logging

PLUGIN_NAME: str = "logging_plugin"
PLUGIN_PRIORITY: PluginPriorityEnum = PluginPriorityEnum.IMMEDIATE

if TYPE_CHECKING:
    from python_stack.core.application import AbstractApplication


def load(application: "AbstractApplication") -> Callable[[Binder], None] | None:
    """
    Load the logging plugin.

    This method is called when the plugin is loaded.
    """

    # Define the configuration method base on the environment,
    # and environment variables

    configure_logging(
        json_logs=application.get_configuration().log_use_json,
        log_level=application.get_configuration().log_level,
    )

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
