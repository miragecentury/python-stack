"""
Provide abstract classes for the application.
"""

from .base import AbstractBaseApplication
from .fastapi import AbstractFastApiApplication
from .plugins import AbstractPluginsApplication

__all__ = [
    "AbstractBaseApplication",
    "AbstractFastApiApplication",
    "AbstractPluginsApplication",
]
