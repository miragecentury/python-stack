"""

"""

from typing import Callable, Tuple

import inject
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    MetricExporter,
    MetricReader,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_INSTANCE_ID,
    SERVICE_NAME,
    SERVICE_VERSION,
    TELEMETRY_SDK_LANGUAGE,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
    SpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from python_stack.core.application.abstract import AbstractApplication
from python_stack.core.utils.importlib import get_path_file_in_package
from python_stack.core.utils.yaml_reader import YamlFileReader
from python_stack.core.utils.inject_helper import inject_or_constructor

from .configs import OpenTelemetryConfiguration

RESOURCE_DATADOG_ENV_ATTRIBUTE = "env"
TELEMETRY_SDK_LANGUAGE_PYTHON = "python"

YAML_FILE_NAME = "application.yaml"


class OpenTelemetryManager:
    """
    OpenTelemetry Manager.
    OpenTelemetry Manager is responsible for managing the OpenTelemetry resources.
    """

    def __init__(
        self,
        configuration: OpenTelemetryConfiguration,
        resource: Resource,
        span_processor: SpanProcessor | None = None,
        span_exporter: SpanExporter | None = None,
        tracer_provider: TracerProvider | None = None,
        meter_provider: MeterProvider | None = None,
    ):

        self._configuration = configuration
        self._resource = resource
        self._span_processor = span_processor
        self._span_exporter = span_exporter
        self._tracer_provider: list[TracerProvider] = [tracer_provider]

    def inject_configure(self, binder: inject.Binder) -> None:
        """
        Configure the OpenTelemetry Manager.
        """
        binder.bind(OpenTelemetryManager, self)
        binder.bind(OpenTelemetryConfiguration, self._configuration)
        binder.bind(Resource, self._resource)
        binder.bind(SpanProcessor, self._span_processor)
        binder.bind(TracerProvider, self._tracer_provider[0])

    def on_shutdown(self) -> None:
        """
        Shutdown the OpenTelemetry Manager.
        """

        # Shutdown the Tracer Providers
        for tracer_provider in self._tracer_provider:
            tracer_provider.force_flush()
            tracer_provider.shutdown()
        # Shudown the Span Processor and Span Exporter
        if self._span_processor:
            self._span_processor.shutdown()
        if self._span_exporter:
            self._span_exporter.shutdown()

    def add_tracer_provider(self, tracer_provider: TracerProvider) -> None:
        """
        Add a Tracer Provider to the OpenTelemetry Manager.
        (This is useful for adding multiple Tracer Providers like for dependencies)
        """
        self._tracer_provider.append(tracer_provider)


class OpenTelemetryManagerFactory:
    """
    Provides a factory for building OpenTelemetry Configurations.
    """

    @classmethod
    def build_opentelemetry_config(
        cls, application: AbstractApplication
    ) -> OpenTelemetryConfiguration:
        """
        Build the OpenTelemetry Config for the application.

        Returns:
            OpenTelemetryConfiguration: The OpenTelemetry Config for the application.
        """

        # Read the OpenTelemetry Configuration from the YAML file
        yaml_reader = YamlFileReader(
            file_path=get_path_file_in_package(
                YAML_FILE_NAME, application.get_application_package()
            ),
            yaml_base_key="opentelemetry",
            use_environment_injection=True,
        )
        opentelemetry_config_data = yaml_reader.read()

        return OpenTelemetryConfiguration(**opentelemetry_config_data)

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
                DEPLOYMENT_ENVIRONMENT: application.get_environment().value,
                TELEMETRY_SDK_LANGUAGE: TELEMETRY_SDK_LANGUAGE_PYTHON,
                # Datadog specific attribute
                RESOURCE_DATADOG_ENV_ATTRIBUTE: application.get_environment().value,
            }
        )

    @classmethod
    def build_trace_stack(
        cls,
        resource: Resource,
        configuration: OpenTelemetryConfiguration,
        span_exporter: SpanExporter | None = None,
    ) -> Tuple[SpanProcessor | None, SpanExporter | None, TracerProvider]:
        """
        Build the Trace Stack.

        Returns:
            Tuple[SpanProcessor, SpanExporter]: The Trace Stack.
        """

        # Build the Tracer Provider
        tracer_provider = TracerProvider(resource=resource)

        if configuration.spans_enabled:

            if span_exporter is None:
                # TODO: Add support for ChannelCredentials
                # TODO: Add support for Compression
                # TODO: Add support for Headers
                # TODO: Add support for Timeout
                span_exporter = OTLPSpanExporter(
                    endpoint=configuration.collector_endpoint,
                    insecure=configuration.collector_endpoint.startswith("http://"),
                )
            # TODO: Add support for max_queue_size, max_export_batch_size,
            # TODO: Add support scheduled_delay, and export_timeout
            if configuration.spans_processor_batch:
                span_processor = BatchSpanProcessor(span_exporter)
            else:
                span_processor = SimpleSpanProcessor(span_exporter)
            tracer_provider.add_span_processor(span_processor)
        else:
            span_processor = None
            span_exporter = None

        return span_processor, span_exporter, tracer_provider

    def __init__(
        self,
        application: AbstractApplication,
        configuration: OpenTelemetryConfiguration | None = None,
    ) -> None:
        """
        Constructor for the OpenTelemetryFactory class.

        Args:
            application (AbstractApplication): The application instance.
            configuration (OpenTelemetryConfiguration): The OpenTelemetry Configuration.
        """

        self._application: AbstractApplication = application

        # Build the OpenTelemetry Configuration
        # It's the only object that must be built in constructor
        # to prevent the application from starting if the configuration is invalid.
        if configuration is None:
            self._opentelemetry_configuration = inject_or_constructor(
                OpenTelemetryConfiguration,
                lambda: self.build_opentelemetry_config(application=application),
            )
        else:
            self._opentelemetry_configuration = configuration

    def build(
        self,
    ) -> OpenTelemetryManager:
        """
        Build the OpenTelemetry Manager.

        Returns:
            OpenTelemetryManager: The OpenTelemetry Manager.
        """
        _resource = self.build_opentelemetry_resource(application=self._application)
        _span_processor, _span_exporter, _tracer_provider = self.build_trace_stack(
            resource=_resource,
            configuration=self._opentelemetry_configuration,
        )
        return OpenTelemetryManager(
            configuration=self._opentelemetry_configuration,
            resource=_resource,
            span_processor=_span_processor,
            span_exporter=_span_exporter,
            tracer_provider=_tracer_provider,
        )
