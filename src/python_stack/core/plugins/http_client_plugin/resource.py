"""
Provides the resource class for the http client plugin.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from httpx import AsyncClient, AsyncHTTPTransport, Limits

from python_stack.core.plugins.http_client_plugin.configs import (
    HttpClientConfig,
)


class HttpClientResource:
    """
    Represents the resource class for the http client plugin.
    """

    def _build_transport(self) -> AsyncHTTPTransport:
        """
        Build the transport for the http client plugin.
        """
        return AsyncHTTPTransport(
            verify=True,  # Verify SSL certificates.
            cert=None,  # Client-side certificates.
            http1=True,  # Enable HTTP/1.1.
            http2=False,  # Enable HTTP/2.
            limits=Limits(
                max_connections=self._config.limits.max_connections,
                max_keepalive_connections=(
                    self._config.limits.max_keepalive_connections,
                ),
                keepalive_expiry=self._config.limits.keepalive_expiry,
            ),
            trust_env=False,  # Trust the environment for proxy settings.
            proxy=None,  # Proxy settings.
            uds=None,  # Unix domain socket settings.
            local_address=None,  # Local address settings.
            retries=self._config.retries,
            socket_options=None,
        )

    def __init__(self, config: HttpClientConfig) -> None:
        """
        Initializes the resource class for the http client plugin.
        """
        self._config: HttpClientConfig = config
        self._pool_in_use: list = []
        self._transport: AsyncHTTPTransport = self._build_transport()

    @asynccontextmanager
    async def acquire_client(
        self, **kwargs
    ) -> AsyncGenerator[AsyncClient, None]:
        """
        Acquire a client from the pool.
        """

        # Override the transport
        if "transport" in kwargs:
            raise ValueError("The transport cannot be overridden.")

        # Set the transport
        kwargs["transport"] = self._transport

        yield AsyncClient(
            **kwargs,
        )
