"""

"""

from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_INSTANCE_ID,
    SERVICE_NAME,
    SERVICE_VERSION,
    Resource,
)

from python_stack.core.application.abstract import AbstractApplication
from python_stack.core.utils.yaml_reader import YamlReader

from .configs import OpenTelemetryConfiguration

RESOURCE_DATADOG_ENV_ATTRIBUTE = "env"


class OpenTelemetryManager:
    pass


class OpenTelemetryManagerFactory:
    """
    Provides a factory for building OpenTelemetry Configurations.
    """

    @classmethod
    def build_opentelemetry_config(cls) -> OpenTelemetryConfiguration:
        """
        Build the OpenTelemetry Config for the application.

        Returns:
            OpenTelemetryConfiguration: The OpenTelemetry Config for the application.
        """

        return

    @classmethod
    def build_opentelemetry_resource(cls, application: AbstractApplication) -> Resource:
        """
        Build the OpenTelemetry Resource for the application.

        Args:
            application (AbstractApplication): The application instance.

        Returns:
            Resource: The OpenTelemetry Resource for the application.
        """

        return Resource(
            attributes={
                SERVICE_NAME: application.MONITORED_RESOURCE_TYPE,
                SERVICE_INSTANCE_ID: application.MONITORED_IDENTIFIER,
                SERVICE_VERSION: application.get_version(),
                DEPLOYMENT_ENVIRONMENT: application.get_environment(),
                # Datadog specific attribute
                RESOURCE_DATADOG_ENV_ATTRIBUTE: application.get_environment(),
            }
        )

    def __init__(
        self,
        application: AbstractApplication,
        opentelemetry_configuration: OpenTelemetryConfiguration = None,
    ) -> None:
        """
        Constructor for the OpenTelemetryFactory class.
        """

        self._application: AbstractApplication = application

        # Build the OpenTelemetry Configuration
        # It's the only object that must be built in constructor
        # to prevent the application from starting if the configuration is invalid.
        if opentelemetry_configuration is None:
            self._opentelemetry_configuration: OpenTelemetryConfiguration = (
                self.build_opentelemetry_config()
            )
        else:
            self._opentelemetry_configuration = opentelemetry_configuration
