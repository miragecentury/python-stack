"""
This module contains the API endpoints for the readiness of the application.
"""

from http import HTTPStatus
import inject
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel


from typing_extensions import Annotated
from python_stack.core.api.tags import MONITORING
from python_stack.core.utils.monitored import ReadinessStatusEnum, MonitoredService

api_v1_monitored_readiness = APIRouter(prefix="/readiness")
api_v2_monitored_readiness = APIRouter(prefix="/readiness")


class MonitoredReadinessResponse(Response, BaseModel):
    """
    The response model for the health status of the application.
    """

    readiness: ReadinessStatusEnum


@api_v1_monitored_readiness.get(
    "",
    response_model=MonitoredReadinessResponse,
    summary="Get the health status of the application.",
    description="Get the health status of the application.",
    tags=[MONITORING],
    responses={
        HTTPStatus.OK.value: {
            "model": MonitoredReadinessResponse,
            "description": "Application is ready",
            "content": {"application/json": {"example": {"readiness": "ready"}}},
        },
        HTTPStatus.SERVICE_UNAVAILABLE.value: {
            "model": MonitoredReadinessResponse,
            "description": "Application is Unhealthy",
            "content": {
                "application/json": {
                    "examples": {
                        "unhealthy": {
                            "summary": "Application is not ready",
                            "value": {"readiness": "not_ready"},
                        },
                        "unknown": {
                            "summary": "Application is Unknown",
                            "value": {"readiness": "unknown"},
                        },
                    }
                }
            },
        },
    },
)
def get_health(
    monitored_service: Annotated[
        MonitoredService, Depends(lambda: inject.instance(MonitoredService))
    ],
    response: MonitoredReadinessResponse,
) -> dict:
    """
    Get the health status of the service.

    Args:
        monitored_service (MonitoredService): The monitored service.
        response (MonitoredHealthResponse): The response object.

    Returns:
        MonitoredHealthResponse: The health status of the service.
    """
    response.readiness = monitored_service.get_readiness_status()
    match (response.health):
        case ReadinessStatusEnum.READY:
            # The health status is ready.
            response.status_code = HTTPStatus.OK
        case ReadinessStatusEnum.NOT_READY:
            # The health status is not_ready.
            response.status_code = HTTPStatus.SERVICE_UNAVAILABLE
        case _:
            # This is the default case, which is used when the health status is unknown.
            # By convention, the health status is set to unknown
            # when the health check fails.
            response.status_code = HTTPStatus.SERVICE_UNAVAILABLE
            response.readiness = ReadinessStatusEnum.UNKNOWN

    return response
