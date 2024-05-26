from fastapi.testclient import TestClient

from python_stack.example.application import Application


class TestApplication:

    def test_application(self):
        _application = Application()
        with TestClient(_application) as _client:

            _response = _client.get("/api/v1/monitored/readiness")
            assert _response.status_code == 200
            assert _response.json() == {"readiness": "ready"}

            _response = _client.get("/api/v1/monitored/health")
            assert _response.status_code == 200
            assert _response.json() == {"health": "healthy"}
