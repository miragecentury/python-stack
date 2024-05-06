"""
Example Application class for the Python Stack.
"""

from inject import Binder

from python_stack.core.application import AbstractApplication


class Application(AbstractApplication):
    """
    Example Application class for the Python Stack.
    """

    _version = "0.1.0"
    _title = "Python Stack Example"
    _description = "Example Python Stack Application"

    def __init__(
        self, fastapi_app=None, environment="development", use_mode_test=False
    ):
        """
        Initializes the Application
        """
        super().__init__(
            fastapi_app, environment, use_mode_test, application_package=__package__
        )

    def _configure_inject(self, binder: Binder) -> None:
        """
        Overrides the parent method to configure the dependency injection container for
        the Application "Example".
        """
        super()._configure_inject(binder)
        binder.bind(Application, self)
