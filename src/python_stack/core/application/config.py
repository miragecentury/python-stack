from pydantic import BaseModel

from .enums import Environment


class AbstractApplicationConfig(BaseModel):
    """
    Represents the configuration for the application.
    """

    environment: Environment
