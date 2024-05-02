"""
Provides the configuration for the application.
"""

from pydantic import BaseModel

from .enums import Environment


class AbstractApplicationConfigServer(BaseModel):
    """
    Represents the configuration for the server.
    """

    host: str
    port: int


class AbstractApplicationConfig(BaseModel):
    """
    Represents the configuration for the application.
    """

    server: AbstractApplicationConfigServer
    environment: Environment
