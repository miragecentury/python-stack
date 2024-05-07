"""
Provide the test for the readiness endpoint.
"""

from fastapi.testclient import TestClient
from units.abstract import TestCaseAbstract

from python_stack.core.utils.monitored.enums import ReadinessStatusEnum


class TestApiMonitoredReadinessSimple(TestCaseAbstract):
    """
    Test case for the readiness endpoint.
    """

    def test_get_readiness(self):
        """
        Test the readiness endpoint.
        """
        with self.build_application() as _application:
            with TestClient(_application) as _client:
                response = _client.get("/api/v1/monitored/readiness")
                assert response.status_code == 200
                assert response.json() == {"readiness": ReadinessStatusEnum.READY.value}
