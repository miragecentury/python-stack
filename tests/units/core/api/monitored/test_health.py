"""
Provide the test cases for the health endpoint.
"""

from fastapi.testclient import TestClient
from units.abstract import TestCaseAbstract

from python_stack.core.utils.monitored.enums import HealthStatusEnum


class TestApiMonitoredHealthSimple(TestCaseAbstract):
    """
    Test case for the health endpoint.
    """

    def test_get_health(self):
        """
        Provide the test case for the health endpoint.
        """

        with TestClient(self.build_application()) as _client:
            response = _client.get("/api/v1/monitored/health")
            assert response.status_code == 200
            assert response.json() == {"health": HealthStatusEnum.HEALTHY.value}
