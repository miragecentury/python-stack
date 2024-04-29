"""
Provides the enums for the monitor module.
"""

from enum import StrEnum


class MonitorTypeEnum(StrEnum):
    """
    Defines the possible types of monitors.
    """

    HEALTH = "health"
    READINESS = "readiness"


class HealthStatusEnum(StrEnum):
    """
    Defines the possible health status of a resource.
    """

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    DISABLED = "disabled"


class ReadinessStatusEnum(StrEnum):
    """
    Defines the possible readiness status of a resource.
    """

    READY = "ready"
    NOT_READY = "not_ready"
    UNKNOWN = "unknown"
    DISABLED = "disabled"
