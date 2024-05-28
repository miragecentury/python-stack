"""
Provides models for the monitored service.
"""

from dataclasses import dataclass

import reactivex

from .enums import (
    HealthStatusEnum,
    MonitorResourceTypeEnum,
    MonitorTypeEnum,
    ReadinessStatusEnum,
)


@dataclass
class MonitoredStatusUpdate:
    """
    Represents a status update for a monitored resource exposed
    through an observable.
    """

    identifier: str
    monitor_type: MonitorTypeEnum
    status: HealthStatusEnum | ReadinessStatusEnum


@dataclass
class MonitoredResource:
    """
    Represents a monitored resource internally in the monitored service.
    """

    types: set[MonitorTypeEnum]
    resource_type: MonitorResourceTypeEnum
    identifier: str
    health_status: HealthStatusEnum | None
    readiness_status: ReadinessStatusEnum | None
    health_subject: reactivex.Subject[HealthStatusEnum] | None
    readiness_subject: reactivex.Subject[ReadinessStatusEnum] | None
