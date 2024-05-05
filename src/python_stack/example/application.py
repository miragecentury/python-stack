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

    def _configure_inject(self, binder: Binder) -> None:
        """
        Overrides the parent method to configure the dependency injection container for
        the Application "Example".
        """
        super()._configure_inject(binder)
        binder.bind(Application, self)
