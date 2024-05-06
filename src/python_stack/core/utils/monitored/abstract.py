"""
Provides the abstract classes for monitored classes.
"""

from abc import ABC

import inject
import reactivex

from .enums import (
    HealthStatusEnum,
    MonitorResourceTypeEnum,
    MonitorTypeEnum,
    ReadinessStatusEnum,
)
from .service import MonitoredService


class AbstractMonitored(ABC):
    """
    Represents a class that is monitored.
    """

    @inject.params(monitored_service=MonitoredService)
    def __init__(self, monitored_service=None) -> None:
        """
        Initializes the AbstractMonitored class.
        """
        # Ensure the monitored service is not None
        assert monitored_service is not None

        super().__init__()
        # Initialize the monitor type subjects
        self._monitor_service: MonitoredService = monitored_service
        self._monitor_type_subjects: set[MonitorTypeEnum] = set()


class AbstractHealthMonitored(AbstractMonitored):
    """
    Represents a class that is monitored for health.
    """

    def __init__(
        self,
        identifier: str,
        initial_health_status: HealthStatusEnum,
        resource_type: MonitorResourceTypeEnum,
    ) -> None:
        """
        Initializes the AbstractHealthMonitored class.
        """

        AbstractMonitored.__init__(self=self)
        # Add the health monitor type to the monitor type subjects
        self._monitor_type_subjects.add(MonitorTypeEnum.HEALTH)
        # Initialize the health status based on the provided initial health status
        self._monitor_health_status: HealthStatusEnum = initial_health_status

        # Register the monitored resource with the monitored service
        self._monitor_health_subject: reactivex.Subject[HealthStatusEnum] = (
            self._monitor_service.register_monitored_resource(
                monitor_type=MonitorTypeEnum.HEALTH,
                resource_type=resource_type,
                identifier=identifier,
                initial_status=initial_health_status,
            )
        )

    def change_health_status(self, new_health_status: HealthStatusEnum) -> None:
        """
        Changes the health status of the monitored resource.
        """

        # Update the health status
        self._monitor_health_status = new_health_status
        # Notify the monitored service of the status change
        self._monitor_health_subject.on_next(new_health_status)


class AbstractReadinessMonitored(AbstractMonitored):
    """
    Represents a class that is monitored for readiness.
    """

    def __init__(
        self,
        identifier: str,
        initial_readiness_status: ReadinessStatusEnum,
        resource_type: MonitorResourceTypeEnum,
    ) -> None:
        """
        Initializes the AbstractReadinessMonitored class.
        """

        AbstractMonitored.__init__(self=self)
        # Add the readiness monitor type to the monitor type subjects
        self._monitor_type_subjects.add(MonitorTypeEnum.READINESS)
        # Initialize the readiness status based on the provided initial readiness status
        self._monitor_readiness_status: ReadinessStatusEnum = initial_readiness_status

        # Register the monitored resource with the monitored service
        self._monitor_readiness_subject: reactivex.Subject[ReadinessStatusEnum] = (
            self._monitor_service.register_monitored_resource(
                monitor_type=MonitorTypeEnum.READINESS,
                resource_type=resource_type,
                identifier=identifier,
                initial_status=initial_readiness_status,
            )
        )

    def change_readiness_status(
        self, new_readiness_status: ReadinessStatusEnum
    ) -> None:
        """
        Changes the readiness status of the monitored resource.
        """

        # Update the readiness status
        self._monitor_readiness_status = new_readiness_status
        # Notify the monitored service of the status change
        self._monitor_readiness_subject.on_next(new_readiness_status)
