"""
Package for creating an Application.
"""

import fastapi
import inject
import uvicorn
from starlette.types import Receive, Scope, Send

from .plugins import AbstractPluginsApplication

from ..utils.monitored import (
    AbstractHealthMonitored,
    AbstractReadinessMonitored,
    HealthStatusEnum,
    ReadinessStatusEnum,
    MonitoredService,
    MonitorResourceTypeEnum,
)

from ..api.monitored import api_v1_monitored, api_v2_monitored


class AbstractApplication(
    AbstractHealthMonitored, AbstractReadinessMonitored, AbstractPluginsApplication
):
    """
    Abstract class for creating an Application.
    """

    # Monitored Constants
    MONITORED_IDENTIFIER: str = "application"
    MONITORED_RESOURCE_TYPE: MonitorResourceTypeEnum = (
        MonitorResourceTypeEnum.APPLICATION
    )

    # Server Constants
    DEFAULT_PORT: int = 8080
    DEFAULT_HOST: str = "0.0.0.0"

    # Inject Constants
    DEFAULT_INJECT_ALLOW_OVERRIDE: bool = False

    # FastAPI Constants
    FASTAPI_EVENT_STARTUP = "startup"
    FASTAPI_EVENT_SHUTDOWN = "shutdown"

    # Class Attributes to be set by the subclass
    _version: str | None = None
    _title: str | None = None
    _description: str | None = None

    def build_uvicorn_config(
        self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT
    ) -> uvicorn.Config:
        """
        Builds a uvicorn configuration object for the FastAPI application.

        Args:
            host (str): The host to bind the server to.
            port (int): The port to bind the server to.

        Returns:
            A uvicorn configuration object.
        """
        return uvicorn.Config(
            app=self.fastapi_app,
            host=host,
            port=port,
            loop="asyncio",
        )

    def _on_startup(self) -> None:
        self.change_readiness_status(ReadinessStatusEnum.READY)

    def _on_shutdown(self) -> None:
        pass

    def __init_fastapi__(self, fastapi_app: fastapi.FastAPI | None = None) -> None:
        """
        Initializes the FastAPI application, creating one if not provided.

        Args:
            fastapi_app (fastapi.FastAPI | None): The FastAPI application
            injected or created.

        Raises:
            AssertionError: If the required class attributes are not set.
        """

        # Ensure that the required class attributes are set by the subclass
        assert self._version is not None, "Version is not set"
        assert self._title is not None, "Name is not set"
        assert self._description is not None, "Description is not set"

        # Create a new FastAPI application if one is not provided
        if fastapi_app is None:
            self.fastapi_app = fastapi.FastAPI(
                title=self._title,
                description=self._description,
                version=self._version,
            )
        else:
            self.fastapi_app: fastapi.FastAPI = fastapi_app

        # Register the startup and shutdown events
        self.fastapi_app.add_event_handler(
            event_type=self.FASTAPI_EVENT_STARTUP, func=self._on_startup
        )
        self.fastapi_app.add_event_handler(
            event_type=self.FASTAPI_EVENT_SHUTDOWN, func=self._on_shutdown
        )

        # Register the monitored API routers
        self.fastapi_app.router.include_router(router=api_v1_monitored)
        self.fastapi_app.router.include_router(router=api_v2_monitored)

        print("FastAPI Application Initialized")

    def _configure_inject(self, binder: inject.Binder) -> None:
        """
        Configures the dependency injection container.

        Args:
            binder (inject.Binder): The dependency injection container.
        """
        binder.bind(cls=AbstractApplication, instance=self)
        binder.bind(cls=fastapi.FastAPI, instance=self.fastapi_app)
        binder.bind(cls=MonitoredService, instance=self._monitored_service)
        # Call the configure method for each plugin
        super()._configure_inject(binder=binder)

    def __init_inject__(self, allow_override: bool = False) -> inject.Injector:
        """
        Initializes the dependency injection container.
        """

        return inject.configure(
            config=self._configure_inject, allow_override=allow_override
        )

    def __init__(
        self,
        fastapi_app: fastapi.FastAPI | None = None,
        allow_override: bool = DEFAULT_INJECT_ALLOW_OVERRIDE,
    ) -> None:
        """
        Initializes the Application
        """

        # Initialize the AbstractPluginsApplication
        AbstractPluginsApplication.__init__(self=self)

        # Initialize the FastAPI application
        self.__init_fastapi__(fastapi_app=fastapi_app)

        # Initialize the MonitoredService
        self._monitored_service = MonitoredService()

        # Initialize the dependency injection container
        self._injector = self.__init_inject__(allow_override=allow_override)

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

    def get_injector(self) -> inject.Injector:
        """
        Gets the dependency injection container.

        Returns:
            The dependency injection container.
        """
        return self._injector

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        This method is called by the ASGI server and
        proxies to the FastAPI application.
        """
        await self.fastapi_app(scope, receive, send)
