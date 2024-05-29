"""
Provides the configuration for the HTTP client plugin.
"""

from typing import TYPE_CHECKING, Annotated, Self

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    PositiveFloat,
    PositiveInt,
    UrlConstraints,
    model_validator,
)

from python_stack.core.utils.importlib import get_path_file_in_package
from python_stack.core.utils.yaml_reader import (
    UnableToReadYamlFileError,
    YamlFileReader,
)

from .exceptions import UnableToBuildConfigError

if TYPE_CHECKING:
    from python_stack.core.application import AbstractApplication

APPLICATION_YAML_CONFIG_BASE_KEY = "resources.http_client"


class HttpClientConfigLimits(BaseModel):
    """
    Represents the limits for the HTTP client plugin.
    """

    max_connections: Annotated[int, PositiveInt] = Field(
        description="The maximum number of connections."
    )
    max_keepalive_connections: Annotated[int, PositiveInt] = Field(
        description="The maximum number of keep-alive connections."
    )
    keepalive_expiry: Annotated[float, PositiveFloat] = Field(
        description="The number of seconds to keep a connection alive."
    )

    @model_validator(mode="after")
    def validate_max_keep_alive_consistancy(self) -> Self:
        """
        Validate the max_keepalive_connections
        is less than or equal to max_connections.
        """
        if self.max_keepalive_connections > self.max_connections:
            raise ValueError(
                "The max_keepalive_connections must be "
                + "less than or equal to max_connections."
            )
        return self


class HttpClientConfig(BaseModel):
    """
    Represents the configuration for the HTTP client plugin.
    """

    DEFAULT_RETRIES: int = 2

    # The timeout for the HTTP client
    timeout: Annotated[int, PositiveInt] = Field(
        description="The timeout for the HTTP client."
    )

    retries: Annotated[int, PositiveInt] = Field(
        default=DEFAULT_RETRIES,
        description="The number of retries for the HTTP client.",
    )

    base_url: Annotated[
        HttpUrl,
        UrlConstraints(allowed_schemes=["https"], host_required=True),
    ] = Field(description="The base URL for the HTTP client.")

    limits: HttpClientConfigLimits


def build_from_application_config(
    application: "AbstractApplication",
    identifier: str,
) -> HttpClientConfig:
    """
    Build the configuration from the application configuration.
    """

    base_key = f"{APPLICATION_YAML_CONFIG_BASE_KEY}.{identifier}"

    try:
        application_yaml_path = get_path_file_in_package(
            "application.yaml", application.APPLICATION_PACKAGE
        )
    except (FileNotFoundError, ImportError) as exception:
        raise UnableToBuildConfigError() from exception

    try:
        application_config_dict = YamlFileReader(
            application_yaml_path, base_key
        ).read()
    except UnableToReadYamlFileError as exception:
        raise UnableToBuildConfigError() from exception

    return HttpClientConfig(**application_config_dict)
