import inject
import json
from fastapi import APIRouter, Depends, Response

from typing_extensions import Annotated
from python_stack.core.utils.monitored.service import MonitoredService

api_v1_monitored_health = APIRouter(prefix="/health")
api_v2_monitored_health = APIRouter(prefix="/health")


@api_v1_monitored_health.get(
    "",
)
def get_health(
    monitored_service: Annotated[
        MonitoredService, Depends(lambda: inject.instance(MonitoredService))
    ]
) -> dict:
    """
    Get the health status of the service.

    Args:
        monitored_service (MonitoredService): The monitored service.

    Returns:
        dict: The health status of the service.
    """
    return Response(
        content=json.dumps({"health": monitored_service.get_health_status()})
    )
