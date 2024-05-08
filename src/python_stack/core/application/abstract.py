"""
Package for creating an Application.
"""

from typing import Callable, Coroutine

import fastapi
import inject


from python_stack.core.application.config import AbstractApplicationConfig
from python_stack.core.application.enums import Environment

from ..api.monitored import api_v1_monitored, api_v2_monitored
from ..utils.importlib import get_path_file_in_package
from ..utils.monitored import (
    AbstractHealthMonitored,
    AbstractReadinessMonitored,
    HealthStatusEnum,
    MonitoredService,
    MonitorResourceTypeEnum,
    ReadinessStatusEnum,
)
from ..utils.yaml_reader import YamlFileReader
from .abstracts.plugins import (
    AbstractPluginsApplication,
    PluginPriorityEnum,
    PluginProtocol,
)
from .abstracts.fastapi import AbstractFastApiApplication


class AbstractApplication(
    AbstractHealthMonitored,
    AbstractReadinessMonitored,
    AbstractPluginsApplication,
    AbstractFastApiApplication,
):
    """
    Abstract class for creating an Application.
    """

    # Monitored Constants
    MONITORED_IDENTIFIER: str = "application"
    MONITORED_RESOURCE_TYPE: MonitorResourceTypeEnum = (
        MonitorResourceTypeEnum.APPLICATION
    )

    plugins_default: list[PluginProtocol | str] = [
        "python_stack.core.plugins.opentelemetry_plugin"
    ]

    def _configure_inject(self, binder: inject.Binder) -> None:
        """
        Configures the dependency injection container.

        Args:
            binder (inject.Binder): The dependency injection container.
        """
        self._inject_binder = binder
        binder.bind(cls=AbstractApplication, instance=self)
        binder.bind(cls=fastapi.FastAPI, instance=self.get_fast_api())
        binder.bind(cls=MonitoredService, instance=self._monitored_service)
        # Call the configure method for each plugin
        super()._configure_inject(binder=binder)

        if self._inject_override_binder is not None:
            binder.install(self._inject_override_binder)

    def __init_inject__(
        self,
        inject_allow_override: bool = False,
    ) -> inject.Injector:
        """
        Initializes the dependency injection container.
        """
        return inject.configure(
            config=self._configure_inject,
            allow_override=inject_allow_override,
            clear=True,
        )

    async def _on_startup(self) -> None:
        """
        The method to be called on FastAPI startup.
        Must be implemented by the subclass and should call the super method.
        """
        self.change_readiness_status(ReadinessStatusEnum.READY)

    async def _on_shutdown(self) -> None:
        """
        The method to be called on FastAPI startup.
        Must be implemented by the subclass and should call the super method.
        """

    def __init__(
        self,
        application_package: str,
        application_configuration: AbstractApplicationConfig = None,
        fastapi_app: fastapi.FastAPI | None = None,
        inject_allow_override: bool = False,
        inject_override_binder: Callable[[inject.Binder], None] = None,
    ) -> None:
        """
        Initializes the Application
        """

        if application_configuration is None:
            application_configuration = AbstractApplicationConfig(
                **YamlFileReader(
                    get_path_file_in_package("application.yaml", application_package),
                    yaml_base_key="application",
                    use_environment_injection=True,
                ).read()
            )

        self._application_package: str = application_package
        self._environment: Environment = application_configuration.environment

        # Initialize the AbstractPluginsApplication
        AbstractPluginsApplication.__init__(self=self)

        self.load(priority=PluginPriorityEnum.IMMEDIATE)

        # Initialize the FastAPI application
        AbstractFastApiApplication.__init__(self=self)
        self.__init_fastapi__(fastapi_app=fastapi_app)
        # Add the monitored api routers
        self.get_fast_api().include_router(api_v1_monitored)
        self.get_fast_api().include_router(api_v2_monitored)

        # Initialize the MonitoredService
        self._monitored_service = MonitoredService()

        self.load(priority=PluginPriorityEnum.NORMAL)
        self.load(priority=PluginPriorityEnum.DELAYED)

        # Initialize the dependency injection container
        self._inject_override_binder: Callable[[inject.Binder], None] = (
            inject_override_binder
        )
        self._inject_binder: inject.Binder | None = None
        self._injector: inject.Injector = self.__init_inject__(
            inject_allow_override=inject_allow_override
        )

        # Initialize the AbstractMonitored classes
        AbstractHealthMonitored.__init__(
            self=self,
            resource_type=self.MONITORED_RESOURCE_TYPE,
            identifier=self.MONITORED_IDENTIFIER,
            initial_health_status=HealthStatusEnum.HEALTHY,
        )
        AbstractReadinessMonitored.__init__(
            self=self,
            resource_type=self.MONITORED_RESOURCE_TYPE,
            identifier=self.MONITORED_IDENTIFIER,
            initial_readiness_status=ReadinessStatusEnum.NOT_READY,
        )
        # Set the health status to healthy
        self.change_health_status(HealthStatusEnum.HEALTHY)

    def get_version(self) -> str:
        """
        Gets the version of the application.

        Returns:
            str: The version of the application.
        """
        return self._version

    def get_environment(self) -> Environment:
        """
        Gets the environment of the application.

        Returns:
            str: The environment of the application.
        """
        return self._environment

    def get_application_package(self) -> str:
        """
        Gets the application package.

        Returns:
            str: The application package.
        """
        return self._application_package
