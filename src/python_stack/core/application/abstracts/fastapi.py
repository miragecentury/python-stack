"""
Provides an abstract class for a FastAPI application.
"""

from abc import ABC, abstractmethod

import uvicorn
from fastapi import FastAPI
from starlette.types import Receive, Scope, Send

from python_stack.core.application.enums import Environment

from . import AbstractBaseApplicationProtocol


class AbstractFastApiApplication(AbstractBaseApplicationProtocol, ABC):
    """
    Provides an abstract class for a FastAPI application.
    Encapsulates the FastAPI application and provides automatic configuration and
    integration.
    """

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

    def __init__(self):
        """
        Initializes the Abstract FastAPI application.
        """
        super().__init__()
        self._fastapi_app: FastAPI = None

    def get_fast_api(self) -> FastAPI:
        """
        Returns the FastAPI application.
        """

        return self._fastapi_app

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

        match (self.get_environment()):
            case Environment.PRODUCTION:
                _access_log = False
            case _:
                _access_log = True

        # TODO: Add support for SSL
        # TODO: Add support for timeouts

        return uvicorn.Config(
            app=self._fastapi_app,
            host=host,
            port=port,
            loop="asyncio",
            log_config=None,
            access_log=_access_log,
        )

    @abstractmethod
    async def _on_startup(self) -> None:
        """
        Method to be called on FastAPI startup.
        Must be implemented by the subclass.
        """
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    async def _on_shutdown(self) -> None:
        """
        Method to be called on FastAPI shutdown.
        Must be implemented by the subclass.
        """
        raise NotImplementedError("Method not implemented")

    def __init_fastapi__(self, fastapi_app: FastAPI | None = None) -> None:
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
            self._fastapi_app = FastAPI(
                title=self._title,
                description=self._description,
                version=self._version,
            )
        else:
            self._fastapi_app: FastAPI = fastapi_app

        # Register the startup and shutdown events
        self._fastapi_app.add_event_handler(
            event_type=self.FASTAPI_EVENT_STARTUP, func=self._on_startup
        )
        self._fastapi_app.add_event_handler(
            event_type=self.FASTAPI_EVENT_SHUTDOWN, func=self._on_shutdown
        )

        print("FastAPI Application Initialized")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        This method is called by the ASGI server and
        proxies to the FastAPI application.
        """
        await self._fastapi_app(scope, receive, send)

    def get_version(self) -> str:
        """
        Gets the version of the application.

        Returns:
            str: The version of the application.
        """
        return self._version
