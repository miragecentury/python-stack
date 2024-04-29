"""
Package for creating an Application.
"""

from abc import ABC

import fastapi
from starlette.types import Receive, Scope, Send


class AbstractApplication(ABC):
    """
    Abstract class for creating an Application.
    """

    # FastAPI Constants
    FASTAPI_EVENT_STARTUP = "startup"
    FASTAPI_EVENT_SHUTDOWN = "shutdown"

    # Class Attributes to be set by the subclass
    _version: str | None = None
    _title: str | None = None
    _description: str | None = None

    def _on_startup(self) -> None:
        pass

    def _on_shutdown(self) -> None:
        pass

    def __init_fastapi__(self, fastapi_app: fastapi.FastAPI | None = None) -> None:
        """
        Initializes the FastAPI application, create one if not provided.

        :param fastapi_app: The FastAPI application injected or created.
        :type fastapi_app: fastapi.FastAPI | None

        :return: None

        :raises AssertionError: If the required class attributes are not set.
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
        else:
            self.fastapi_app: fastapi.FastAPI = fastapi_app

        # Register the startup and shutdown events
        self.fastapi_app.add_event_handler(
            event_type=self.FASTAPI_EVENT_STARTUP, func=self._on_startup
        )
        self.fastapi_app.add_event_handler(
            event_type=self.FASTAPI_EVENT_SHUTDOWN, func=self._on_shutdown
        )

    def __init__(self, fastapi_app: fastapi.FastAPI | None = None):
        self.__init_fastapi__(fastapi_app)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        This method is called by the ASGI server and
        proxies to the FastAPI application.
        """
        await self.fastapi_app(scope, receive, send)
