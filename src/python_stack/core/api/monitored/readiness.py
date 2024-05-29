"""
This module contains the API endpoints for the readiness of the application.
"""

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Response
from pydantic import BaseModel

from python_stack.core.api.tags import MONITORING
from python_stack.core.utils.inject_helper import inject_depends
from python_stack.core.utils.monitored import (
    MonitoredService,
    ReadinessStatusEnum,
)

api_v1_monitored_readiness = APIRouter(prefix="/readiness")
api_v2_monitored_readiness = APIRouter(prefix="/readiness")


class MonitoredReadinessModel(BaseModel):
    """
    The response model for the health status of the application.
    """

    readiness: ReadinessStatusEnum


@api_v1_monitored_readiness.get(
    "",
    response_model=MonitoredReadinessModel,
    summary="Get the health status of the application.",
    description="Get the health status of the application.",
    tags=[MONITORING],
    responses={
        HTTPStatus.OK.value: {
            "model": MonitoredReadinessModel,
            "description": "Application is ready",
            "content": {
                "application/json": {"example": {"readiness": "ready"}}
            },
        },
        HTTPStatus.SERVICE_UNAVAILABLE.value: {
            "model": MonitoredReadinessModel,
            "description": "Display the readiness status of the application.",
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
def get_readiness(
    monitored_service: Annotated[
        MonitoredService, inject_depends(MonitoredService)
    ],
    response: Response,
) -> MonitoredReadinessModel:
    """
    Get the health status of the service.

    Args:
        monitored_service (MonitoredService): The monitored service.
        response (MonitoredHealthResponse): The response object.

    Returns:
        MonitoredHealthResponse: The health status of the service.
    """
    monitored_readiness_model = MonitoredReadinessModel(
        readiness=monitored_service.get_readiness_status()
    )
    match (monitored_readiness_model.readiness):
        case ReadinessStatusEnum.READY:
            # The health status is ready.
            response.status_code = HTTPStatus.OK
        case ReadinessStatusEnum.NOT_READY:
            # The health status is not_ready.
            response.status_code = HTTPStatus.SERVICE_UNAVAILABLE
        case _:
            # This is the default case, which is used when the health
            # status is unknown.
            # By convention, the health status is set to unknown
            # when the health check fails.
            response.status_code = HTTPStatus.SERVICE_UNAVAILABLE
            monitored_readiness_model.readiness = ReadinessStatusEnum.UNKNOWN

    return monitored_readiness_model
