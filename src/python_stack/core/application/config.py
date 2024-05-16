"""
Provides the configuration for the application.
"""

import logging
import os
from typing import Any

from pydantic import BaseModel, model_validator

from .enums import Environment


class AbstractApplicationConfigServer(BaseModel):
    """
    Represents the configuration for the server.
    """

    host: str
    port: int


class AbstractApplicationConfig(BaseModel):
    """
    Represents the configuration for the application.
    """

    server: AbstractApplicationConfigServer
    environment: Environment
    log_level: int
    log_use_json: bool

    @model_validator(mode="before")
    @classmethod
    def validate_and_transform_log_level(cls, data: Any) -> Any:
        """
        Validates and transforms the log level.
        """

        # If the log level is not set, then set it based on the environment
        if data.get("log_level", None) is None:
            data["log_level"] = os.getenv("LOG_LEVEL", None)

        # if the log level is not set with the environment variable,
        # then set it based on the environment in configuration
        if data.get("log_level", None) is None:
            match (Environment(data["environment"])):
                case Environment.DEVELOPMENT:
                    data["log_level"] = logging.DEBUG
                case Environment.TESTING:
                    data["log_level"] = logging.INFO
                case Environment.STAGING:
                    data["log_level"] = logging.INFO
                case Environment.PRODUCTION:
                    data["log_level"] = logging.INFO
                case _:
                    data["log_level"] = logging.INFO

        # If the log level is a string, then convert it to the integer value
        if isinstance(data["log_level"], str):
            data["log_level"] = logging.getLevelNamesMapping()[
                str(data["log_level"]).upper()
            ]

        return data

    @model_validator(mode="before")
    @classmethod
    def validate_and_transform_log_use_json(cls, data: Any) -> Any:
        """
        Validates and transforms the log use json.
        """

        if "environment" in data:
            if not isinstance(data["environment"], Environment):
                _env_name = str(data["environment"]).upper()
                data["environment"] = Environment[_env_name]

        if "log_use_json" not in data:
            match (data["environment"]):
                case Environment.DEVELOPMENT:
                    data["log_use_json"] = False
                case Environment.TESTING:
                    data["log_use_json"] = False
                case Environment.STAGING:
                    data["log_use_json"] = True
                case Environment.PRODUCTION:
                    data["log_use_json"] = True
                case _:
                    data["log_use_json"] = False

        return data
