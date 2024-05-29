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
        host = "localhost"
        port = 8080
        server = AbstractApplicationConfigServer(host=host, port=port)
        assert server.host == host
        assert server.port == port


class TestAbstractApplicationConfig:
    """
    Validate the AbstractApplicationConfig.
    """

    def test_abstract_application_config(self) -> None:
        """
        Test the AbstractApplicationConfig.
        """
        server = AbstractApplicationConfigServer(host="localhost", port=8080)
        environment = "DEVELOPMENT"
        log_level = 10
        log_use_json = True
        config = AbstractApplicationConfig(
            server=server,
            environment=environment,
            log_level=log_level,
            log_use_json=log_use_json,
        )
        assert config.server == server
        assert str(config.environment).upper() == environment
        assert config.log_level == log_level
        assert config.log_use_json == log_use_json
