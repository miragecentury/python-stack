"""
Abstract class for a basic application.
"""

from abc import ABC
from typing import Protocol

from python_stack.core.application.config import AbstractApplicationConfig
from python_stack.core.application.enums import Environment
from python_stack.core.utils.importlib import get_path_file_in_package
from python_stack.core.utils.inject_helper import inject_or_constructor
from python_stack.core.utils.yaml_reader import YamlFileReader


class AbstractBaseApplicationProtocol(Protocol):
    """
    Provides an Interface for a basic application.
    """

    def get_environment(self) -> Environment:
        """
        Gets the environment of the application.

        Returns:
            str: The environment of the application.
        """

    def get_application_package(self) -> str:
        """
        Gets the application package.

        Returns:
            str: The application package.
        """

    def get_configuration(self) -> AbstractApplicationConfig:
        """
        Gets the configuration of the application.

        Returns:
            AbstractApplicationConfig: The configuration of the application.
        """


class AbstractBaseApplication(ABC):
    """
    Provides an abstract class for a basic
    """

    def __init__(
        self,
        application_package: str,
    ) -> None:
        self._configuration: AbstractApplicationConfig = inject_or_constructor(
            cls=AbstractApplicationConfig,
            # pylint: disable=unnecessary-lambda
            constructor_callable=lambda: AbstractApplicationConfig(
                **YamlFileReader(
                    file_path=get_path_file_in_package(
                        filename="application.yaml", package=application_package
                    ),
                    yaml_base_key="application",
                    use_environment_injection=True,
                ).read()
            ),
        )

        self._application_package: str = application_package
        self._environment: Environment = self._configuration.environment

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

    def get_configuration(self) -> AbstractApplicationConfig:
        """
        Gets the configuration of the application.

        Returns:
            AbstractApplicationConfig: The configuration of the application.
        """
        return self._configuration
