"""
Package for API endpoints.
"""

import fastapi

api_v1 = fastapi.APIRouter(
    prefix="/api/v1",
    tags=["API v1"],
)

api_v2 = fastapi.APIRouter(
    prefix="/api/v2",
    tags=["API v2"],
)
