"""
Provides an abstract class for creating an application with plugins.
"""

import importlib
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
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
    def load(self, application) -> Callable[[inject.Binder], None] | None:
        """
        Load the plugin.

        This method is called when the plugin is loaded.
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

    plugins_default: list[PluginProtocol | str] = list()

    def _validate_plugins(self, plugins: list[PluginProtocol]) -> None:
        """
        Check if the package are instances of PluginProtocol.

        Args:
            plugins (list[PluginProtocol]): A list of plugins to be used
            by the application.

        Raises:
            TypeError: If a plugin in the list is not an
            instance of PluginProtocol.
        """
        for plugin in plugins:
            if not isinstance(plugin, PluginProtocol):
                raise TypeError(
                    f"Plugin {plugin} is not an instance of PluginProtocol"
                )

    def _order_plugins_by_priority(
        self, plugins: list[PluginProtocol]
    ) -> dict[PluginPriorityEnum, list[PluginProtocol]]:
        """
        Order the plugins by priority.

        Args:
            plugins (list[PluginProtocol]): A list of plugins to be used
            by the application.

        Returns:
            dict[PluginPriorityEnum, list[PluginProtocol]]: A dictionary
            with the plugins ordered by priority.
        """
        ordered_plugins: dict[PluginPriorityEnum, list[PluginProtocol]] = (
            defaultdict(list)
        )

        for plugin in plugins:
            ordered_plugins[plugin.PLUGIN_PRIORITY].append(plugin)

        return ordered_plugins

    def __init__(self, plugins: list[PluginProtocol] | None = None) -> None:
        """
        Constructor for the AbstractPluginsApplication class.

        Args:
            plugins (list[PluginProtocol]): A list of plugins to be used
            by the application.

        Raises:
            TypeError: If a plugin in the set is not
            an instance of PluginProtocol.
        """

        if plugins is not None:
            self.plugins_default.extend(plugins)

        self._plugins: list[PluginProtocol] = []

        for plugin in self.plugins_default:
            if isinstance(plugin, str):
                plugin_module = importlib.import_module(plugin)
                self._plugins.append(plugin_module)
            else:
                self._plugins.append(plugin)

        # Validate the plugins (raises TypeError if invalid)
        self._validate_plugins(self._plugins)
        # Order the plugins by priority
        self._plugins_ordered: dict[
            PluginPriorityEnum, list[PluginProtocol]
        ] = self._order_plugins_by_priority(self._plugins)
        # Initialize the ordered inject configure dictionary for later use
        self._plugins_ordered_inject_configure: dict[
            PluginPriorityEnum, list[Callable[[inject.Binder], None]]
        ] = defaultdict(list)

    def load(self, priority: PluginPriorityEnum) -> None:
        """
        Load the plugins in the order of priority.

        Args:
            priority (PluginPriorityEnum): The priority of the plugins to load.
        """
        for plugin in self._plugins_ordered[priority]:
            calleable = plugin.load(self)
            if calleable is not None:
                self._plugins_ordered_inject_configure[priority].append(
                    calleable
                )

    def _configure_inject(self, binder: inject.Binder) -> None:
        """
        Configures the dependency injection container.

        Args:
            binder (inject.Binder): The dependency injection container.
        """
        # Call the configure method for each plugin in order of priority
        for (
            _,
            plugins_inject_configure,
        ) in self._plugins_ordered_inject_configure.items():
            for inject_configure in plugins_inject_configure:
                if inject_configure is not None:
                    binder.install(inject_configure)
