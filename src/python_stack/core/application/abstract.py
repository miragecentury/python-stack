"""
Package for creating an Application.
"""

from logging.config import IDENTIFIER

import fastapi
import inject
import uvicorn
from starlette.types import Receive, Scope, Send

from python_stack.core.utils.monitored.abstract import (
    AbstractHealthMonitored,
    AbstractReadinessMonitored,
)
from python_stack.core.utils.monitored.enums import (
    HealthStatusEnum,
    ReadinessStatusEnum,
)
from python_stack.core.utils.monitored.service import (
    MonitoredService,
    MonitorResourceTypeEnum,
)


class AbstractApplication(AbstractHealthMonitored, AbstractReadinessMonitored):
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

    # FastAPI Constants
    FASTAPI_EVENT_STARTUP = "startup"
    FASTAPI_EVENT_SHUTDOWN = "shutdown"

    # Class Attributes to be set by the subclass
    _version: str | None = None
    _title: str | None = None
    _description: str | None = None

    def build_uvicorn_config(self) -> uvicorn.Config:
        """
        Builds a uvicorn configuration object for the FastAPI application.

        Returns:
            A uvicorn configuration object.
        """
        return uvicorn.Config(
            app=self.fastapi_app,
            host=self._host,
            port=self._port,
            loop="asyncio",
        )

    def _on_startup(self) -> None:
        pass

    def _on_shutdown(self) -> None:
        pass

    def __init_fastapi__(self, fastapi_app: fastapi.FastAPI | None = None) -> None:
        """
        Initializes the FastAPI application, creating one if not provided.

        Args:
            fastapi_app (fastapi.FastAPI | None): The FastAPI application injected or created.

        Raises:
            AssertionError: If the required class attributes are not set.
        """

        # Ensure that the required class attributes are set by the subclass
        assert self._version is not None, "Version is not set"
        assert self._title is not None, "Name is not set"
        assert self._description is not None, "Description is not set"

        # Create a new FastAPI application if one is not provided
        if fastapi_app is None:
            fastapi_app = fastapi.FastAPI(
                title=self._title,
                description=self._description,
                version=self._version,
            )

        self.fastapi_app: fastapi.FastAPI = fastapi_app

        # Register the startup and shutdown events
        self.fastapi_app.add_event_handler(
            event_type=self.FASTAPI_EVENT_STARTUP, func=self._on_startup
        )
        self.fastapi_app.add_event_handler(
            event_type=self.FASTAPI_EVENT_SHUTDOWN, func=self._on_shutdown
        )

    def __init_inject__(self) -> inject.Injector:
        """
        Initializes the dependency injection container.
        """

        def configure(binder: inject.Binder) -> None:
            binder.bind(cls=AbstractApplication, instance=self)
            binder.bind(cls=fastapi.FastAPI, instance=self.fastapi_app)
            binder.bind(cls=MonitoredService, instance=self._monitored_service)

        return inject.configure(config=configure)

    def __init__(
        self,
        fastapi_app: fastapi.FastAPI | None = None,
        host: str | None = DEFAULT_HOST,
        port: int | None = DEFAULT_PORT,
    ) -> None:
        """
        Initializes the Application
        """

        # Set the host and port for the server
        self._host = host
        self._port = port

        # Initialize the FastAPI application
        self.__init_fastapi__(fastapi_app=fastapi_app)

        # Initialize the MonitoredService
        self._monitored_service = MonitoredService()

        # Initialize the dependency injection container
        self._injector = self.__init_inject__()

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

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        This method is called by the ASGI server and
        proxies to the FastAPI application.
        """
        await self.fastapi_app(scope, receive, send)
