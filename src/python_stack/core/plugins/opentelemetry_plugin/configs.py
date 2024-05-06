"""
Configuration for the OpenTelemetry plugin.
"""

from enum import StrEnum, auto

from pydantic import BaseModel, Field, model_validator

from python_stack.core.utils.importlib import get_path_file_in_package
from python_stack.core.utils.yaml_reader import YamlFileReader

OPENTELEMETRY_CONFIGURATION_APPLICATION_YAML_KEY = "opentelemetry"


class OpenTelemetryConfigurationPropagationMode(StrEnum):
    """
    Enum for the OpenTelemetry Configuration Propagation Mode.
    """

    DISABLED = auto()
    B3 = auto()


class OpenTelemetryConfiguration(BaseModel):
    """
    Configuration for OpenTelemetry.
    """

    DEFAULT_COLLECTOR_ENDPOINT = "http://localhost:4317"
    DEFAULT_ENABLED = False
    DEFAULT_METRICS_ENABLED = False
    DEFAULT_TRACES_ENABLED = False

    enabled: bool = Field(
        default=DEFAULT_ENABLED, description="Whether OpenTelemetry is enabled."
    )
    metrics_enabled: bool = Field(
        default=DEFAULT_METRICS_ENABLED,
        description="Whether OpenTelemetry metrics are enabled.",
    )
    traces_enabled: bool = Field(
        default=DEFAULT_TRACES_ENABLED,
        description="Whether OpenTelemetry traces are enabled.",
    )
    propagation_mode: OpenTelemetryConfigurationPropagationMode = Field(
        default=OpenTelemetryConfigurationPropagationMode.DISABLED,
        description="The propagation mode for OpenTelemetry.",
    )

    collector_endpoint: str = Field(
        default=DEFAULT_COLLECTOR_ENDPOINT,
        description="The URL of the OpenTelemetry collector.",
    )

    @model_validator(mode="after")
    def validate_enabled_consistency(self) -> None:
        """
        Validate that the enabled flag is consistent with the metrics and traces flags.
        """
        # If metrics or traces are enabled, OpenTelemetry must be enabled.
        if (self.metrics_enabled or self.traces_enabled) and not self.enabled:
            raise ValueError(
                "Metrics and traces can only be enabled if OpenTelemetry is enabled."
            )

        # If OpenTelemetry is enabled, either metrics or traces must be enabled.
        if self.enabled and not (self.metrics_enabled or self.traces_enabled):
            raise ValueError(
                "OpenTelemetry must have either metrics or traces enabled."
            )

    @model_validator(mode="after")
    def validate_propagation_mode_consistency(self) -> None:
        """
        Validate that the propagation mode is consistent with the enabled flag.
        """
        # Propagation mode can only be enabled if OpenTelemetry is enabled.
        if (
            self.propagation_mode != OpenTelemetryConfigurationPropagationMode.DISABLED
            and not self.enabled
        ):
            raise ValueError(
                "Propagation mode can only be enabled if OpenTelemetry is enabled."
            )


class OpenTelemetryConfigurationAsYamlFile(YamlFileReader[OpenTelemetryConfiguration]):

    def __init__(self) -> None:
        super().__init__(
            file_path=get_path_file_in_package(
                "application.yaml",
            ),
            yaml_base_key=OPENTELEMETRY_CONFIGURATION_APPLICATION_YAML_KEY,
            use_environment_injection=True,
        )
