"""
Provide the test cases for the health endpoint.
"""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from inject import Binder
from units.abstract import TestCaseAbstract

from python_stack.core.utils.monitored.enums import HealthStatusEnum
from python_stack.core.utils.monitored.service import MonitoredService


class TestApiMonitoredHealthSimple(TestCaseAbstract):
    """
    Test case for the health endpoint.
    """

    @pytest.mark.parametrize(
        "health_status, expected_status_code",
        [
            (HealthStatusEnum.HEALTHY, 200),
            (HealthStatusEnum.UNHEALTHY, 503),
            (HealthStatusEnum.UNKNOWN, 503),
        ],
    )
    def test_get_health(
        self, health_status: HealthStatusEnum, expected_status_code: int
    ):
        """
        Provide the test case for the health endpoint.
        """

        _monitored_service_mock: MonitoredService = Mock()

        def inject_override_binder_test(binder: Binder):
            """
            Overrides the parent method to configure the dependency injection container for
            the Application "Test".
            """
            binder.bind(cls=MonitoredService, instance=_monitored_service_mock)

        _monitored_service_mock.get_health_status.return_value = health_status

        with self.build_application(
            inject_override_binder=inject_override_binder_test
        ) as _application:
            with TestClient(_application) as _client:
                response = _client.get("/api/v1/monitored/health")
                assert response.status_code == expected_status_code
                assert response.json() == {"health": health_status.value}
