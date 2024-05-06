"""
This module contains the API endpoints for the health of the application.
"""

from http import HTTPStatus

from fastapi import APIRouter, Response
from pydantic import BaseModel
from typing_extensions import Annotated

from python_stack.core.api.tags import MONITORING
from python_stack.core.utils.fastapi_inject import inject_depends
from python_stack.core.utils.monitored import HealthStatusEnum, MonitoredService

api_v1_monitored_health = APIRouter(prefix="/health")
api_v2_monitored_health = APIRouter(prefix="/health")


class MonitoredHealthModel(BaseModel):
    """
    The response model for the health status of the application.
    """

    health: HealthStatusEnum


@api_v1_monitored_health.get(
    "",
    response_model=MonitoredHealthModel,
    tags=[MONITORING],
    summary="Get the health status of the application.",
    description="Get the health status of the application.",
    responses={
        HTTPStatus.OK.value: {
            "model": MonitoredHealthModel,
            "description": "Application is Healthy",
            "content": {"application/json": {"example": {"health": "healthy"}}},
        },
        HTTPStatus.SERVICE_UNAVAILABLE.value: {
            "model": MonitoredHealthModel,
            "description": "Application is Unhealthy",
            "content": {
                "application/json": {
                    "examples": {
                        "unhealthy": {
                            "summary": "Application is Unhealthy",
                            "value": {"health": "unhealthy"},
                        },
                        "unknown": {
                            "summary": "Application is Unknown",
                            "value": {"health": "unknown"},
                        },
                    }
                }
            },
        },
    },
)
def get_health(
    response: Response,
    monitored_service: Annotated[MonitoredService, inject_depends(MonitoredService)],
) -> MonitoredHealthModel:
    """
    Get the health status of the service.

    Args:
        monitored_service (MonitoredService): The monitored service.
        response (MonitoredHealthResponse): The response object.

    Returns:
        MonitoredHealthResponse: The health status of the service.
    """
    _response = MonitoredHealthModel(health=monitored_service.get_health_status())
    match (_response.health):
        case HealthStatusEnum.HEALTHY:
            # The health status is healthy.
            response.status_code = HTTPStatus.OK
        case HealthStatusEnum.UNHEALTHY:
            # The health status is unhealthy.
            response.status_code = HTTPStatus.SERVICE_UNAVAILABLE
        case _:
            # This is the default case, which is used when the health status is unknown.
            # By convention, the health status is set to unknown
            # when the health check fails.
            response.status_code = HTTPStatus.SERVICE_UNAVAILABLE
            _response.health = HealthStatusEnum.UNKNOWN

    return _response
