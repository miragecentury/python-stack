"""
Package for API endpoints.
"""

import fastapi

from .example import example_v1_api_router, example_v2_api_router

# V1 API(s) ====================================================================

api_v1 = fastapi.APIRouter(
    prefix="/api/v1",
    tags=["API v1"],
)


api_v1.include_router(example_v1_api_router)

# V2 API(s) ====================================================================

api_v2 = fastapi.APIRouter(
    prefix="/api/v2",
    tags=["API v2"],
)

api_v2.include_router(example_v2_api_router)

#
