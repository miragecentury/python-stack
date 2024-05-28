"""
Provides the Environment enum class.
"""

from enum import StrEnum, auto


class Environment(StrEnum):
    """
    Represents the environment in which the application is running.

    Development: The application is running in a development environment.
    We expect the application to be running
    on a developer's machine with console logs enabled.

    Testing: The application is running in a testing environment.

    Staging: The application is running in a staging environment
    before production.

    Production: The application is running in a production environment.
    """

    DEVELOPMENT = auto()
    TESTING = auto()
    STAGING = auto()
    PRODUCTION = auto()
