"""
Provides a service for registering and managing monitored resources 
to expose health and readiness status through api endpoints.
"""

from typing import Dict

import reactivex

from .enums import (
    HealthStatusEnum,
    MonitorResourceTypeEnum,
    MonitorTypeEnum,
    ReadinessStatusEnum,
)
from .models import MonitoredResource, MonitoredStatusUpdate


class HealthStatusServiceResolver:
    """
    Provides a service for resolving the health status
    based on the monitored resources.
    """

    def __init__(
        self, monitored_resources: dict[str, MonitoredResource]
    ) -> None:
        """
        Initialize the health status service resolver
        with the monitored resources.
        """
        self._monitored_resources: Dict[str, MonitoredResource] = (
            monitored_resources
        )

    def resolve(self) -> HealthStatusEnum:
        """
        Resolve the health status based on the monitored resources.
        """
        health_status = HealthStatusEnum.HEALTHY

        # Check if any resource has a status of UNHEALTHY
        for resource in self._monitored_resources.values():
            if MonitorTypeEnum.HEALTH not in resource.types:
                # Skip resources that are not health monitored
                continue
            # If any resource is unhealthy, the global status is unhealthy
            if resource.health_status == HealthStatusEnum.UNHEALTHY:
                health_status = HealthStatusEnum.UNHEALTHY
                break

        return health_status


class ReadinessStatusServiceResolver:
    """
    Provides a service for resolving the readiness status
    based on the monitored resources.
    """

    def __init__(
        self, monitored_resources: dict[str, MonitoredResource]
    ) -> None:
        """
        Initialize the readiness status service resolver
        with the monitored resources.
        """
        self._monitored_resources: Dict[str, MonitoredResource] = (
            monitored_resources
        )

    def resolve(self) -> ReadinessStatusEnum:
        """
        Resolve the readiness status based on the monitored resources.
        """
        readiness_status = ReadinessStatusEnum.READY

        # Check if any resource has a status of NOT_READY
        for resource in self._monitored_resources.values():
            if MonitorTypeEnum.READINESS not in resource.types:
                # Skip resources that are not readiness monitored
                continue
            if resource.readiness_status == ReadinessStatusEnum.NOT_READY:
                readiness_status = ReadinessStatusEnum.NOT_READY
                break

        return readiness_status


class MonitoredService:
    """
    Provides a service for registering and managing monitored resources
    and calculating the health and readiness status based on the resources.
    """

    health_resolver: HealthStatusServiceResolver
    readiness_resolver: ReadinessStatusServiceResolver

    def __init__(self) -> None:
        self._monitored_resources: Dict[str, MonitoredResource]
        self._monitored_resources = {}
        self._health_status: HealthStatusEnum
        self._health_status = HealthStatusEnum.UNKNOWN
        self._readiness_status: ReadinessStatusEnum
        self._readiness_resolver = ReadinessStatusEnum.UNKNOWN

    def get_health_status(self) -> HealthStatusEnum:
        """
        Get the health status of the monitored resources.
        """
        return self._health_status

    def get_readiness_status(self) -> ReadinessStatusEnum:
        """
        Get the readiness status of the monitored resources.
        """
        return self._readiness_status

    def _calculate_health_status(self) -> None:
        """
        Calculate the health status based on the monitored resources.
        """
        self._health_status = HealthStatusServiceResolver(
            monitored_resources=self._monitored_resources
        ).resolve()

    def _calculate_readiness_status(self) -> None:
        """
        Calculate the readiness status based on the monitored resources.
        """

        self._readiness_status = ReadinessStatusServiceResolver(
            monitored_resources=self._monitored_resources
        ).resolve()

    @classmethod
    def _validate_association_of_type_and_status(
        cls,
        monitor_type: MonitorTypeEnum,
        status: HealthStatusEnum | ReadinessStatusEnum,
    ) -> None:
        """
        Validate the association of the monitor type and status.

        Args:
            monitor_type (MonitorTypeEnum): The type of monitor to validate.
            status (HealthStatusEnum | ReadinessStatusEnum): The status
            to validate.

        Raises:
            ValueError: If the monitor type is not supported.
            ValueError: If the initial status is not a valid status
            for the monitor type.
        """
        # Validate the initial status based on the monitor type
        match monitor_type:
            case MonitorTypeEnum.HEALTH:
                if status not in HealthStatusEnum or not isinstance(
                    status, HealthStatusEnum
                ):
                    raise ValueError(
                        f"Initial status {status} is "
                        + "not a valid HealthStatusEnum."
                    )
            case MonitorTypeEnum.READINESS:
                if status not in ReadinessStatusEnum or not isinstance(
                    status, ReadinessStatusEnum
                ):
                    raise ValueError(
                        f"Initial status {status} is not a valid "
                        + "ReadinessStatusEnum."
                    )
            case _:
                raise ValueError(
                    f"Monitor type {monitor_type} is not supported."
                )

    def _handle_status_update(
        self, status_updated: MonitoredStatusUpdate
    ) -> None:
        """
        Receive and handle a status update for a monitored resource.

        Args:
            status_updated (MonitoredStatusUpdate): The status update to handle.

        Raises:
            ValueError: If the monitor type is not supported.
            ValueError: If the status is not a valid status
            for the monitor type.
            ValueError: If the resource is not registered
            with the monitored service.

        """

        # Validations ========================================
        try:
            self._validate_association_of_type_and_status(
                monitor_type=status_updated.monitor_type,
                status=status_updated.status,
            )
        except ValueError as e:
            raise e

        if self._monitored_resources.get(status_updated.identifier) is None:
            raise ValueError(
                f"Resource {status_updated.identifier} is not registered "
                + "with the monitored service."
            )

        # Actions ============================================

        # Update the status based on the monitor type
        match status_updated.monitor_type:
            case MonitorTypeEnum.HEALTH:
                self._monitored_resources[
                    status_updated.identifier
                ].health_status = status_updated.status
                self._calculate_health_status()
            case MonitorTypeEnum.READINESS:
                self._monitored_resources[
                    status_updated.identifier
                ].readiness_status = status_updated.status
                self._calculate_readiness_status()

    def _register_monitored_resource_subject(
        self,
        identifier: str,
        monitor_type: MonitorTypeEnum,
    ) -> reactivex.Subject[MonitoredStatusUpdate]:
        """
        Create and subscribe to a subject for the monitored resource
        with the given identifier and monitor type to simplify
        status updates for the resource.

        Args:
            identifier (str): The unique identifier for the resource.
            monitor_type (MonitorTypeEnum): The type of monitor to register
            the resource with.

        Returns:
            reactivex.Subject[MonitoredStatusUpdate]: The subject for
            the monitored resource.

        """

        subject = reactivex.Subject[MonitoredStatusUpdate]()
        subject.subscribe(
            lambda status: self._handle_status_update(
                MonitoredStatusUpdate(
                    identifier=identifier,
                    monitor_type=monitor_type,
                    status=status,
                )
            )
        )

        return subject

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
            ValueError: If the resource is already registered
            as the same monitor type.
        """

        # Validations ========================================
        try:
            self._validate_association_of_type_and_status(
                monitor_type=monitor_type,
                status=initial_status,
            )
        except ValueError as e:
            raise e

        # Ensure that the resource does not already exist
        resource: MonitoredResource | None = self._monitored_resources.get(
            identifier, None
        )

        # If the resource exists, ensure that it
        # is not already registered as the same monitor type
        if resource is not None:
            if monitor_type in resource.types:
                raise ValueError(
                    f"Resource {identifier} is already registered "
                    + "as a {monitor_type} resource."
                )

        # Actions ============================================

        # If the MonitoredResource does not exist, create it
        if resource is None:
            resource = MonitoredResource(
                types=set(),
                resource_type=resource_type,
                identifier=identifier,
                health_status=None,
                readiness_status=None,
                health_subject=None,
                readiness_subject=None,
            )

        # Add the monitor type to the resource
        resource.types.add(monitor_type)

        # Register the monitored resource subject
        subject: reactivex.Subject[MonitoredStatusUpdate] = (
            self._register_monitored_resource_subject(
                identifier=identifier,
                monitor_type=monitor_type,
            )
        )

        # Set the initial status based on the monitor type
        match monitor_type:
            case MonitorTypeEnum.HEALTH:
                resource.health_status = initial_status
                resource.health_subject = subject
            case MonitorTypeEnum.READINESS:
                resource.readiness_status = initial_status
                resource.readiness_subject = subject

        # Update the monitored resources
        self._monitored_resources[identifier] = resource

        # Emit the initial status
        subject.on_next(initial_status)

        return subject
