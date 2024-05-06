"""
This module contains the code to configure the OpenTelemetry plugin.
"""

from inject import Binder

from python_stack.core.application.plugins import PluginPriorityEnum

PLUGIN_NAME: str = "opentelemetry_plugin"
PLUGIN_PRIORITY: PluginPriorityEnum = PluginPriorityEnum.IMMEDIATE


def load() -> None:
    """
    Load the OpenTelemetry plugin.

    This method is called when the plugin is loaded.
    """
    pass


def configure(binder: Binder) -> None:
    """
    Configure the injector with the OpenTelemetry plugin related bindings.

    Args:
        binder (Binder): The binder object to configure the injector.
    """
    pass


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
