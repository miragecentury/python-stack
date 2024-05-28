"""
Example Application class for the Python Stack.
"""

from typing import Callable

import inject
from inject import Binder

from python_stack.core.application import AbstractApplication


class Application(AbstractApplication):
    """
    Example Application class for the Python Stack.
    """

    APPLICATION_PACKAGE = __package__
    _version = "0.1.0"
    _title = "Python Stack Example"
    _description = "Example Python Stack Application"

    def __init__(
        self,
        fastapi_app=None,
        inject_override_binder: Callable[[inject.Binder], None] | None = None,
    ):
        """
        Initializes the Application
        """
        super().__init__(
            fastapi_app=fastapi_app,
            inject_override_binder=inject_override_binder,
        )

    def _configure_inject(self, binder: Binder) -> None:
        """
        Overrides the parent method to configure the dependency
        injection container for the Application "Example".
        """
        super()._configure_inject(binder)
        binder.bind(Application, self)
