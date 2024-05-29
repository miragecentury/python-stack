"""
Provide an abstract class for unit tests.
"""

from abc import ABC
from collections.abc import Callable, Generator
from contextlib import contextmanager

import inject

from python_stack.core.application import AbstractApplication
from python_stack.core.application.config import (
    AbstractApplicationConfig,
    AbstractApplicationConfigServer,
)
from python_stack.core.application.enums import Environment
from python_stack.core.plugins.opentelemetry_plugin.configs import (
    OpenTelemetryConfiguration,
)


class TestCaseAbstract(ABC):
    """
    Abstract class for unit tests.
    """

    _application_config: AbstractApplicationConfig = AbstractApplicationConfig(
        server=AbstractApplicationConfigServer(
            host="localhost",
            port=8000,
        ),
        environment=Environment.TESTING,
    )

    _opentelemetry_config: OpenTelemetryConfiguration = (
        OpenTelemetryConfiguration(enabled=False)
    )

    @contextmanager
    def build_application(
        self,
        inject_override_binder: Callable[[inject.Binder], None] | None = None,
    ) -> Generator[AbstractApplication, None, None]:
        """
        Provides an instance of the AbstractApplication class.
        """

        class Application(AbstractApplication):
            """
            Application class for testing.
            """

            APPLICATION_PACKAGE: str | None = __package__
            _version = "1.0.0"
            _title = "Test Application"
            _description = "Application for testing."

        def inject_override_binder_test(binder: inject.Binder) -> None:
            """
            Overrides the parent method to configure the dependency
            injection container for the Application "Test".
            """
            binder.bind(
                cls=OpenTelemetryConfiguration,
                instance=self._opentelemetry_config,
            )
            binder.bind(
                cls=AbstractApplicationConfig, instance=self._application_config
            )
            if inject_override_binder is not None:
                binder.install(inject_override_binder)

        # Clear the inject configuration and configure
        # the inject_override_binder_test.
        # This is done to allow the test to provide the injected value
        # before the application re-configure inject.
        inject.configure(inject_override_binder_test, clear=True)

        # use_mode_test=True is used to allow the test
        # to override injected value.
        application = Application(
            inject_allow_override=True,
            inject_override_binder=inject_override_binder_test,
        )

        yield application

        # Clear the inject configuration to avoid conflicts with other tests.
        inject.clear()
