"""
Test the MonitoredService class.
"""

import pytest
import reactivex

from python_stack.core.utils.monitored.enums import (
    HealthStatusEnum,
    MonitorResourceTypeEnum,
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
        Validate the association of the monitor type and status
        for health status.
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
        Validate the association of the monitor type and status
        for invalid status.
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
            (MonitorTypeEnum.READINESS),
        ],
    )
    def test_validate_association_of_type_and_status_invalid_monitor_type(
        self,
        monitor_type: str,
    ):
        """
        Validate the association of the monitor type and status
        for invalid monitor type.
        Raise is expected.
        """

        with pytest.raises(ValueError):
            # pylint: disable=protected-access
            MonitoredService._validate_association_of_type_and_status(
                monitor_type=monitor_type, status=HealthStatusEnum.HEALTHY
            )

        with pytest.raises(ValueError):
            monitored_service = MonitoredService()
            monitored_service.register_monitored_resource(
                monitor_type=monitor_type,
                initial_status=HealthStatusEnum.HEALTHY,
                resource_type=MonitorResourceTypeEnum.APPLICATION,
                identifier="test",
            )

    def test_validate_not_duplicate_registration(self):
        """
        Validate the not duplicate registration of the monitored resource.
        """

        monitor_service = MonitoredService()

        monitor_resource = {
            "monitor_type": MonitorTypeEnum.HEALTH,
            "initial_status": HealthStatusEnum.HEALTHY,
            "resource_type": MonitorResourceTypeEnum.APPLICATION,
            "identifier": "test",
        }

        subject = monitor_service.register_monitored_resource(
            **monitor_resource
        )

        assert isinstance(subject, reactivex.Subject)

        with pytest.raises(ValueError):
            monitor_service.register_monitored_resource(**monitor_resource)
