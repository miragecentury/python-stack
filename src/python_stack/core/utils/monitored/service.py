"""
Provides a service for registering and managing monitored resources 
to expose health and readiness status through api endpoints.
"""

from typing import Dict

import reactivex
from pydantic import BaseModel, ConfigDict

# pylint: disable=unused-wildcard-import, wildcard-import
from .enums import *


class MonitoredStatusUpdate(BaseModel):
    """
    Represents a status update for a monitored resource exposed through an observable.
    """

    identifier: str
    monitor_type: MonitorTypeEnum
    status: HealthStatusEnum | ReadinessStatusEnum


class MonitoredResource(BaseModel):
    """
    Represents a monitored resource internally in the monitored service.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    types: set[MonitorTypeEnum]
    resource_type: MonitorResourceTypeEnum
    identifier: str
    health_status: HealthStatusEnum | None
    readiness_status: ReadinessStatusEnum | None
    health_subject: reactivex.Subject[HealthStatusEnum] | None
    readiness_subject: reactivex.Subject[ReadinessStatusEnum] | None


class MonitoredService:
    """
    Provides a service for registering and managing monitored resources
    and calcu
    """

    def __init__(self) -> None:
        self._monitored_resources: Dict[str, MonitoredResource] = {}

    def _calculate_health_status(self) -> None:
        pass

    def _calculate_readiness_status(self) -> None:
        pass

    def _handle_status_update(self, status_updated: MonitoredStatusUpdate):

        if self._monitored_resources.get(status_updated.identifier) is None:
            raise ValueError(
                f"Resource {status_updated.identifier} is not registered "
                + "with the monitored service."
            )
        match status_updated.monitor_type:
            case MonitorTypeEnum.HEALTH:
                self._monitored_resources[status_updated.identifier].health_status = (
                    status_updated.status
                )

            case MonitorTypeEnum.READINESS:
                self._monitored_resources[
                    status_updated.identifier
                ].readiness_status = status_updated.status
            case _:
                raise ValueError(
                    f"Monitor type {status_updated.monitor_type} is not supported."
                )

    def _register_monitored_resource_subject(
        self,
        identifier: str,
        monitor_type: MonitorTypeEnum,
    ) -> reactivex.Subject[MonitoredStatusUpdate]:

        _subject = reactivex.Subject[MonitoredStatusUpdate]()
        _subject.subscribe(
            lambda status: self._handle_status_update(
                MonitoredStatusUpdate(
                    identifier=identifier,
                    monitor_type=monitor_type,
                    status=status,
                )
            )
        )

        return _subject

    def register_monitored_resource(
        self,
        monitor_type: MonitorTypeEnum,
        resource_type: MonitorResourceTypeEnum,
        identifier: str,
        initial_status: HealthStatusEnum | ReadinessStatusEnum,
    ) -> reactivex.Subject[HealthStatusEnum | ReadinessStatusEnum]:
        """
        Register a monitored resource with
        the given monitor type, resource type, identifier, and initial status.

        Args:
            monitor_type (MonitorTypeEnum):
            The type of monitor to register the resource with.
            resource_type (MonitorResourceTypeEnum):
            The type of resource being monitored.
            identifier (str): The unique identifier for the resource.
            initial_status (HealthStatusEnum | ReadinessStatusEnum):
            The initial status of the resource.

        Returns:


        Raises:
            ValueError: If the monitor type is not supported.
            ValueError: If the initial status is not a valid status
            for the monitor type.
            ValueError: If the resource is already registered as the same monitor type.
        """

        # Validate the initial status based on the monitor type
        match monitor_type:
            case MonitorTypeEnum.HEALTH:
                if initial_status not in HealthStatusEnum:
                    raise ValueError(
                        f"Initial status {initial_status} is not a valid HealthStatusEnum."
                    )
            case MonitorTypeEnum.READINESS:
                if initial_status not in ReadinessStatusEnum:
                    raise ValueError(
                        f"Initial status {initial_status} is not a valid ReadinessStatusEnum."
                    )
            case _:
                raise ValueError(f"Monitor type {monitor_type} is not supported.")

        # Ensure that the resource does not already exist
        _resource = self._monitored_resources.get(identifier, None)

        # If the resource exists, ensure that it
        # is not already registered as the same monitor type
        if _resource is not None:
            if monitor_type in _resource.types:
                raise ValueError(
                    f"Resource {identifier} is already registered as a {monitor_type} resource."
                )
        else:
            _resource = MonitoredResource(
                types=set(),
                resource_type=resource_type,
                identifier=identifier,
                health_status=None,
                readiness_status=None,
                health_subject=None,
                readiness_subject=None,
            )

        # Add the monitor type to the resource
        _resource.types.add(monitor_type)

        # Register the monitored resource subject
        _subject = self._register_monitored_resource_subject(
            identifier=identifier,
            monitor_type=monitor_type,
        )

        # Set the initial status based on the monitor type
        match monitor_type:
            case MonitorTypeEnum.HEALTH:
                _resource.health_status = initial_status
                _resource.health_subject = _subject
            case MonitorTypeEnum.READINESS:
                _resource.readiness_status = initial_status
                _resource.readiness_subject = _subject

        # Update the monitored resources
        self._monitored_resources[identifier] = _resource

        # Emit the initial status
        _subject.on_next(initial_status)

        return _subject
