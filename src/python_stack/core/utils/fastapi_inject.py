"""
Helper functions for FastAPI and Inject library integration.
"""

from typing import Any

import inject
from fastapi import Depends


def inject_depends(cls: type) -> Any:
    """
    Provide dependency through inject library.

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
