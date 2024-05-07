"""
Provide an abstract class for unit tests.
"""

from abc import ABC
from typing import Callable

import inject

from python_stack.core.application import AbstractApplication
from python_stack.core.application.config import (
    AbstractApplicationConfig,
    AbstractApplicationConfigServer,
)
from python_stack.core.application.enums import Environment


class TestCaseAbstract(ABC):
    """
    Abstract class for unit tests.
    """

    def build_application(
        self, inject_override_binder: Callable[[inject.Binder], None] = None
    ) -> AbstractApplication:
        """
        Provides an instance of the AbstractApplication class.
        """

        class Application(AbstractApplication):
            """
            Application class for testing.
            """

            _version = "1.0.0"
            _title = "Test Application"
            _description = "Application for testing."

        _application_config = AbstractApplicationConfig(
            server=AbstractApplicationConfigServer(
                host="localhost",
                port=8000,
            ),
            environment=Environment.TESTING,
        )

        def inject_override_binder_test(binder: inject.Binder) -> None:
            """
            Overrides the parent method to configure the dependency injection container for
            the Application "Test".
            """
            if inject_override_binder is not None:
                binder.install(inject_override_binder)

        # use_mode_test=True is used to allow the test to override injected value.
        return Application(
            application_package=__package__,
            application_configuration=_application_config,
            use_mode_test=True,
            inject_override_binder=inject_override_binder_test,
        )
