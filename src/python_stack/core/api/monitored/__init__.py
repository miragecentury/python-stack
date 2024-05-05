"""
Package for monitored API.
"""

from fastapi import APIRouter

from .health import api_v1_monitored_health, api_v2_monitored_health
from .readiness import api_v1_monitored_readiness, api_v2_monitored_readiness

api_v1_monitored = APIRouter(prefix="/api/v1/monitored")
api_v2_monitored = APIRouter(prefix="/api/v2/monitored")

api_v1_monitored.include_router(router=api_v1_monitored_health)
api_v2_monitored.include_router(router=api_v2_monitored_health)

api_v1_monitored.include_router(router=api_v1_monitored_readiness)
api_v2_monitored.include_router(router=api_v2_monitored_readiness)
