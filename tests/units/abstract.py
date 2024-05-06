"""
Provide an abstract class for unit tests.
"""

from abc import ABC

from python_stack.core.application import AbstractApplication


class TestCaseAbstract(ABC):
    """
    Abstract class for unit tests.
    """

    def build_application(
        self,
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

        # use_mode_test=True is used to allow the test to override injected value.
        return Application(application_package=__package__, use_mode_test=True)
