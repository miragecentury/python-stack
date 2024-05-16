"""
Test cases for the core.application.config module.
"""

from python_stack.core.application.config import (
    AbstractApplicationConfig,
    AbstractApplicationConfigServer,
)


class TestAbstractApplicationConfigServer:
    """
    Validate the AbstractApplicationConfigServer.
    """

    def test_abstract_application_config_server(self) -> None:
        """
        Test the AbstractApplicationConfigServer.
        """
        _host = "localhost"
        _port = 8080
        _server = AbstractApplicationConfigServer(host=_host, port=_port)
        assert _server.host == _host
        assert _server.port == _port


class TestAbstractApplicationConfig:
    """
    Validate the AbstractApplicationConfig.
    """

    def test_abstract_application_config(self) -> None:
        """
        Test the AbstractApplicationConfig.
        """
        _server = AbstractApplicationConfigServer(host="localhost", port=8080)
        _environment = "DEVELOPMENT"
        _log_level = 10
        _log_use_json = True
        _config = AbstractApplicationConfig(
            server=_server,
            environment=_environment,
            log_level=_log_level,
            log_use_json=_log_use_json,
        )
        assert _config.server == _server
        assert str(_config.environment).upper() == _environment
        assert _config.log_level == _log_level
        assert _config.log_use_json == _log_use_json
