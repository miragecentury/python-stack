"""
Helper functions for FastAPI and Inject library integration.
"""

from collections.abc import Callable
from typing import Any

import inject
from fastapi import Depends


def inject_depends(cls: type) -> Any:
    """
    Provide dependency for FastAPI through inject library.

    Example:
    ```python
        # Needed Code without it
        monitored_service: Annotated[
            MonitoredService, Depends(lambda: inject.instance(MonitoredService))
        ],
        # Replaced with
        monitored_service: Annotated[
            MonitoredService, InjectDepends(MonitoredService)
        ],
    ```

    Args:
        cls (type): The class to provide as a dependency.

    Returns:
        Any: The dependency provided by the inject library.
    """
    return Depends(dependency=lambda: inject.instance(cls), use_cache=False)


def inject_or_constructor(
    cls: type, constructor_callable: Callable[[], Any]
) -> Any:
    """
    Return the instance of the class if it exists in the inject library,
    otherwise return the callable result.

    Args:
        cls (type): The class to provide as a dependency.
        constructor_collable (Callable[[], Any]): The callable to return
        if the class is not found.

    Returns:
        Any: The dependency provided by the inject library
        or the callable result.
    """
    try:
        return inject.instance(cls)
    except inject.InjectorException:
        return constructor_callable()


def inject_or_none(cls: type) -> Any | None:
    """
    Return the instance of the class if it exists in the inject library or None.

    Args:
        cls (type): The class to provide as a dependency.

    Returns:
        Any | None: The dependency provided by the inject library or None.
    """
    try:
        return inject.instance(cls)
    except inject.InjectorException:
        return None
