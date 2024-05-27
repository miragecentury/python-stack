"""
Provides example API endpoints.
"""

from uuid import UUID

import fastapi

from .tags import EXAMPLE

example_v1_api_router = fastapi.APIRouter(prefix="/example", tags=[EXAMPLE])
example_v2_api_router = fastapi.APIRouter(prefix="/example", tags=[EXAMPLE])


@example_v1_api_router.post(
    path="",
    tags=[EXAMPLE],
    summary="Create an example.",
    description="Create an example.",
    responses={
        201: {
            "description": "Example created.",
            "content": {
                "application/json": {
                    "example": {
                        "example": "example",
                    }
                }
            },
        },
    },
)
def create_example(response: fastapi.Response):
    """
    Create an example.
    """
    response.status_code = 201
    return {"example": "example"}


@example_v1_api_router.get(
    path="/{example_id}",
    tags=[EXAMPLE],
    summary="Get an example.",
    description="Get an example.",
    responses={
        200: {
            "description": "Example retrieved.",
            "content": {
                "application/json": {
                    "example": {
                        "example": "example",
                    }
                }
            },
        },
    },
)
def get_example(example_id: UUID):
    """
    Get an example.
    """
    return {"example": "example"}
