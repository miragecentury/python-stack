"""
Provides the abstract classes for monitored classes.
"""

from abc import ABC

from .enums import HealthStatusEnum, MonitorTypeEnum, ReadinessStatusEnum


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

    def __init__(
        self, monitored_initial_health: HealthStatusEnum = HealthStatusEnum.UNKNOWN
    ) -> None:
        """
        Initializes the AbstractHealthMonitored class.
        """
        super().__init__()
        # Add the health monitor type to the monitor type subjects
        self._monitor_type_subjects.add(MonitorTypeEnum.HEALTH)
        # Initialize the health status based on the provided initial health status
        self._monitor_health_status: HealthStatusEnum = monitored_initial_health


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
