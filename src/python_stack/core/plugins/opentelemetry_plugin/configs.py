"""
Configuration for the OpenTelemetry plugin.
"""

from enum import StrEnum, auto
from typing import Self

from pydantic import BaseModel, Field, model_validator

OPENTELEMETRY_CONFIGURATION_APPLICATION_YAML_KEY = "opentelemetry"


class OpenTelemetryConfigurationPropagationMode(StrEnum):
    """
    Enum for the OpenTelemetry Configuration Propagation Mode.
    """

    DISABLED = auto()
    B3 = auto()


DEFAULT_COLLECTOR_ENDPOINT = "http://localhost:4317"
DEFAULT_ENABLED = False
DEFAULT_TRACES_ENABLED = False
DEFAULT_TRACES_BATCH = False
DEFAULT_METRICS_ENABLED = False


class OpenTelemetryConfiguration(BaseModel):
    """
    Configuration for OpenTelemetry.
    """

    enabled: bool = Field(
        default=DEFAULT_ENABLED, description="Whether OpenTelemetry is enabled."
    )
    metrics_enabled: bool = Field(
        default=DEFAULT_METRICS_ENABLED,
        description="Whether OpenTelemetry metrics are enabled.",
    )
    spans_enabled: bool = Field(
        default=DEFAULT_TRACES_ENABLED,
        description="Whether OpenTelemetry traces are enabled.",
    )

    spans_processor_batch: bool = Field(
        default=DEFAULT_TRACES_BATCH,
        description="Whether to use the batch span processor."
        + "If False, the simple span processor is used.",
    )

    propagation_mode: OpenTelemetryConfigurationPropagationMode = Field(
        default=OpenTelemetryConfigurationPropagationMode.DISABLED,
        description="The propagation mode for OpenTelemetry.",
    )

    metrics_interval: float = Field(
        default=2000,
        description=(
            "The interval in millisecond to send metrics to the collector."
        ),
    )

    collector_endpoint: str = Field(
        default=DEFAULT_COLLECTOR_ENDPOINT,
        description="The URL of the OpenTelemetry collector.",
    )

    @model_validator(mode="after")
    def validate_enabled_consistency(self) -> Self:
        """
        Validate that the enabled flag is consistent
        with the metrics and traces flags.
        """
        # If metrics or traces are enabled, OpenTelemetry must be enabled.
        if (self.metrics_enabled or self.spans_enabled) and not self.enabled:
            raise ValueError(
                "Metrics and traces can only be enabled "
                + "if OpenTelemetry is enabled."
            )

        # If OpenTelemetry is enabled, either metrics or traces must be enabled.
        if self.enabled and not (self.metrics_enabled or self.spans_enabled):
            raise ValueError(
                "OpenTelemetry must have either metrics or traces enabled."
            )

        return self

    @model_validator(mode="after")
    def validate_metrics_interval_consistency(self) -> Self:
        """
        Validate that the metrics interval is greater than 0.
        """
        if self.metrics_interval <= 0:
            raise ValueError("Metrics interval must be greater than 0.")

        return self

    @model_validator(mode="after")
    def validate_propagation_mode_consistency(self) -> Self:
        """
        Validate that the propagation mode is consistent with the enabled flag.
        """
        # Propagation mode can only be enabled if OpenTelemetry is enabled.
        if (
            self.propagation_mode
            != OpenTelemetryConfigurationPropagationMode.DISABLED
            and not self.enabled
        ):
            raise ValueError(
                "Propagation mode can only be enabled "
                + "if OpenTelemetry is enabled."
            )

        return self
