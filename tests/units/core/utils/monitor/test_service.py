"""
Test the MonitoredService class.
"""

import pytest

from python_stack.core.utils.monitored.enums import (
    HealthStatusEnum,
    MonitorTypeEnum,
    ReadinessStatusEnum,
)
from python_stack.core.utils.monitored.service import MonitoredService


class TestMonitoredServiceValidationMethods:
    """
    Test the validation methods of the MonitoredService class.
    """

    @pytest.mark.parametrize(
        "monitor_type, status",
        [
            (MonitorTypeEnum.HEALTH, HealthStatusEnum.HEALTHY),
            (MonitorTypeEnum.HEALTH, HealthStatusEnum.UNHEALTHY),
            (MonitorTypeEnum.HEALTH, HealthStatusEnum.UNKNOWN),
            (MonitorTypeEnum.READINESS, ReadinessStatusEnum.READY),
            (MonitorTypeEnum.READINESS, ReadinessStatusEnum.NOT_READY),
            (MonitorTypeEnum.READINESS, ReadinessStatusEnum.UNKNOWN),
        ],
    )
    def test_validate_association_of_type_and_status_health_status(
        self,
        monitor_type: MonitorTypeEnum,
        status: HealthStatusEnum | ReadinessStatusEnum,
    ):
        """
        Validate the association of the monitor type and status for health status.
        No Raise is expected.
        """

        # pylint: disable=protected-access
        MonitoredService._validate_association_of_type_and_status(
            monitor_type=monitor_type, status=status
        )

    @pytest.mark.parametrize(
        "monitor_type, status",
        [
            (MonitorTypeEnum.HEALTH, ReadinessStatusEnum.READY),
            (MonitorTypeEnum.HEALTH, ReadinessStatusEnum.NOT_READY),
            (MonitorTypeEnum.HEALTH, ReadinessStatusEnum.UNKNOWN),
            (MonitorTypeEnum.READINESS, HealthStatusEnum.HEALTHY),
            (MonitorTypeEnum.READINESS, HealthStatusEnum.UNHEALTHY),
            (MonitorTypeEnum.READINESS, HealthStatusEnum.UNKNOWN),
        ],
    )
    def test_validate_association_of_type_and_status_invalid_status(
        self,
        monitor_type: MonitorTypeEnum,
        status: HealthStatusEnum | ReadinessStatusEnum,
    ):
        """
        Validate the association of the monitor type and status for invalid status.
        Raise is expected.
        """

        with pytest.raises(ValueError):
            # pylint: disable=protected-access
            MonitoredService._validate_association_of_type_and_status(
                monitor_type=monitor_type, status=status
            )

    @pytest.mark.parametrize(
        "monitor_type",
        [
            ("HEALTH"),
            ("READINESS"),
            ("NOT-VALID-TYPE"),
        ],
    )
    def test_validate_association_of_type_and_status_invalid_monitor_type(
        self,
        monitor_type: str,
    ):
        """
        Validate the association of the monitor type and status for invalid monitor type.
        Raise is expected.
        """

        with pytest.raises(ValueError):
            # pylint: disable=protected-access
            MonitoredService._validate_association_of_type_and_status(
                monitor_type=monitor_type, status=HealthStatusEnum.HEALTHY
            )
