"""
Provides an abstract class for creating an application with plugins.
"""

import inject
from abc import ABC

from typing import Protocol


class PluginProtocol(Protocol):
    """ """

    def configure(self, binder: inject.Binder) -> None:
        """
        Provides a way to configure injector with the plugin related bindings.

        Args:
            binder (Binder): The binder object to configure the injector.

        """
        raise NotImplementedError


class AbstractPluginsApplication(ABC):
    """
    Provides an abstract class for creating an application with plugins.
    """

    default_plugins: set[PluginProtocol] = set()

    def _validate_plugins(self, plugins: set[PluginProtocol]) -> None:
        for plugin in plugins:
            if not isinstance(plugin, PluginProtocol):
                raise TypeError(f"Plugin {plugin} is not an instance of PluginProtocol")

    def __init__(self, plugins: set[PluginProtocol] | None = None) -> None:
        """
        Constructor for the AbstractPluginsApplication class.

        Args:
            plugins (set[PluginProtocol]): A set of plugins to be used by the application.

        Raises:
            TypeError: If a plugin in the set is not an instance of PluginProtocol.
        """

        if plugins is not None:
            self._plugins: set[PluginProtocol] = self.default_plugins.union(plugins)
        else:
            self._plugins: set[PluginProtocol] = self.default_plugins

        # Validate the plugins (raises TypeError if invalid)
        self._validate_plugins(self._plugins)

    def _configure_inject(self, binder: inject.Binder) -> None:
        """
        Configures the dependency injection container.

        Args:
            binder (inject.Binder): The dependency injection container.
        """

        for plugin in self._plugins:
            plugin.configure(binder)
