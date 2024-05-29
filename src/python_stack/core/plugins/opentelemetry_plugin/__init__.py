"""
This module contains the code to configure the OpenTelemetry plugin.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from inject import Binder

from python_stack.core.application.abstracts.plugins import PluginPriorityEnum

PLUGIN_NAME: str = "opentelemetry_plugin"
PLUGIN_PRIORITY: PluginPriorityEnum = PluginPriorityEnum.NORMAL


from .factories import OpenTelemetryManager, OpenTelemetryManagerFactory

if TYPE_CHECKING:
    from python_stack.core.application import AbstractApplication


def load(application: "AbstractApplication") -> Callable[[Binder], None]:
    """
    Load the OpenTelemetry plugin.

    This method is called when the plugin is loaded.
    """
    manager = OpenTelemetryManagerFactory(application=application).build()
    manager.instrument_fastapi(application.get_fastapi())
    return manager.inject_configure


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
