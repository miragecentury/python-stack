"""
This module contains the code to configure the OpenTelemetry plugin.
"""

from typing import TYPE_CHECKING, Callable

from inject import Binder

from python_stack.core.application.plugins import PluginPriorityEnum

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
    _manager = OpenTelemetryManagerFactory(application=application).build()
    _manager.instrument_fastapi(application.fastapi_app)
    return _manager.inject_configure


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
