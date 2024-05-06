"""
Provides an abstract class for creating an application with plugins.
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from enum import IntEnum
from typing import Protocol, runtime_checkable

import inject


class PluginPriorityEnum(IntEnum):
    """
    Define the priority of the plugin
    for the loading, configuration, and execution order.
    """

    IMMEDIATE = 0
    NORMAL = 1
    DELAYED = 2


@runtime_checkable
class PluginProtocol(Protocol):
    """
    Provide an interface for creating a plugin and controlling the behavior.
    """

    PLUGIN_NAME: str

    PLUGIN_PRIORITY: PluginPriorityEnum

    @abstractmethod
    def load(self) -> None:
        """
        Load the plugin.

        This method is called when the plugin is loaded.
        """
        raise NotImplementedError

    @abstractmethod
    def configure(self, binder: inject.Binder) -> None:
        """
        Provides a way to configure injector with the plugin related bindings.

        Args:
            binder (Binder): The binder object to configure the injector.

        """
        raise NotImplementedError

    @abstractmethod
    def on_startup(self) -> None:
        """
        Provides a way to execute code when the application starts.

        This method is called when the application starts.
        """
        raise NotImplementedError

    @abstractmethod
    def on_shutdown(self) -> None:
        """
        Provides a way to execute code when the application stops.

        This method is called when the application stops.
        """
        raise NotImplementedError


class AbstractPluginsApplication(ABC):
    """
    Provides an abstract class for creating an application with plugins.
    """

    default_plugins: set[PluginProtocol] = set()

    def _validate_plugins(self, plugins: set[PluginProtocol]) -> None:
        """
        Check if the package are instances of PluginProtocol.

        Args:
            plugins (set[PluginProtocol]): A set of plugins to be used
            by the application.

        Raises:
            TypeError: If a plugin in the set is not an instance of PluginProtocol.
        """
        for plugin in plugins:
            if not isinstance(plugin, PluginProtocol):
                raise TypeError(f"Plugin {plugin} is not an instance of PluginProtocol")

    def _order_plugins_by_priority(
        self, plugins: set[PluginProtocol]
    ) -> dict[PluginPriorityEnum, list[PluginProtocol]]:
        """
        Order the plugins by priority.

        Args:
            plugins (set[PluginProtocol]): A set of plugins to be used
            by the application.

        Returns:
            dict[PluginPriorityEnum, list[PluginProtocol]]: A dictionary with the
            plugins ordered by priority.
        """
        ordered_plugins: dict[PluginPriorityEnum, list[PluginProtocol]] = defaultdict(
            list
        )

        for plugin in plugins:
            ordered_plugins[plugin.PLUGIN_PRIORITY].append(plugin)

        return ordered_plugins

    def __init__(self, plugins: set[PluginProtocol] | None = None) -> None:
        """
        Constructor for the AbstractPluginsApplication class.

        Args:
            plugins (set[PluginProtocol]): A set of plugins to be used
            by the application.

        Raises:
            TypeError: If a plugin in the set is not an instance of PluginProtocol.
        """

        if plugins is not None:
            self._plugins: set[PluginProtocol] = self.default_plugins.union(plugins)
        else:
            self._plugins: set[PluginProtocol] = self.default_plugins

        # Validate the plugins (raises TypeError if invalid)
        self._validate_plugins(self._plugins)
        # Order the plugins by priority
        self._plugins_ordered: dict[PluginPriorityEnum, list[PluginProtocol]] = (
            self._order_plugins_by_priority(self._plugins)
        )

    def _configure_inject(self, binder: inject.Binder) -> None:
        """
        Configures the dependency injection container.

        Args:
            binder (inject.Binder): The dependency injection container.
        """
        # Call the configure method for each plugin in order of priority
        for _priority, plugins in self._plugins_ordered.items():
            for plugin in plugins:
                plugin.configure(binder)
