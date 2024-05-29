"""
Provide basic test for the application instanciation.
"""

from fastapi.testclient import TestClient

from python_stack.example.application import Application


class TestApplication:
    """
    Test the application instanciation.
    """

    def test_application(self):
        """
        Test the application instanciation.
        """

        application = Application()
        with TestClient(application) as client:

            response = client.get("/api/v1/monitored/readiness")
            assert response.status_code == 200
            assert response.json() == {"readiness": "ready"}

            response = client.get("/api/v1/monitored/health")
            assert response.status_code == 200
            assert response.json() == {"health": "healthy"}
