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

    def __init__(self) -> None:
        """
        Initializes the AbstractMonitored class.
        """
        super().__init__()
        # Initialize the monitor type subjects
        self._monitor_type_subjects: set[MonitorTypeEnum] = set()


class AbstractHealthMonitored(AbstractMonitored):
    """
    Represents a class that is monitored for health.
    """

    @inject.params(monitored_service=MonitoredService)
    def __init__(
        self,
        identified: str,
        initial_health_status: HealthStatusEnum,
        resource_type: MonitorResourceTypeEnum,
        monitored_service: MonitoredService,
    ) -> None:
        """
        Initializes the AbstractHealthMonitored class.
        """
        super().__init__()
        # Add the health monitor type to the monitor type subjects
        self._monitor_type_subjects.add(MonitorTypeEnum.HEALTH)
        # Initialize the health status based on the provided initial health status
        self._monitor_health_status: HealthStatusEnum = initial_health_status

        # Register the monitored resource with the monitored service
        self._monitor_health_subject: reactivex.Subject[HealthStatusEnum] = (
            monitored_service.register_monitored_resource(
                monitor_type=MonitorTypeEnum.HEALTH,
                resource_type=resource_type,
                identifier=identified,
                initial_status=initial_health_status,
            )
        )


class AbstractReadinessMonitored(AbstractMonitored):
    """
    Represents a class that is monitored for readiness.
    """

    def __init__(
        self,
        monitored_initial_readiness: ReadinessStatusEnum = ReadinessStatusEnum.UNKNOWN,
    ) -> None:
        """
        Initializes the AbstractReadinessMonitored class.
        """
        super().__init__()
        # Add the readiness monitor type to the monitor type subjects
        self._monitor_type_subjects.add(MonitorTypeEnum.READINESS)
        # Initialize the readiness status based on the provided initial readiness status
        self._monitor_readiness_status: ReadinessStatusEnum = (
            monitored_initial_readiness
        )
