"""
Provides a class for reading YAML files and converting them to Pydantic models.
"""

import os
import re
from pathlib import Path

from fastapi.background import P
from yaml import SafeLoader


class UnableToReadYamlFileError(Exception):
    """
    Raised when there is an error reading a YAML file.
    """

    def __init__(self, file_path: Path, message: str) -> None:
        """
        Initializes the exception.

        Args:
          file_path (str): The path to the YAML file.
          message (str): The error message.
        """
        super().__init__(f"Error reading YAML file: {file_path} - {message}")


class YamlFileReader:
    """
    Handles reading YAML files and converting them to Pydantic models.
    """

    re = re.compile(r"\${([A-Za-z0-9\-\_]+):?([A-Za-z0-9\-\_]*)?}")

    def __init__(
        self,
        file_path: Path,
        yaml_base_key: str | None = None,
        use_environment_injection: bool = True,
    ) -> None:
        """
        Initializes the YAML file reader.

        Args:
          file_path (str): The path to the YAML file.
          yaml_base_key (str | None, optional): The base key
          in the YAML file to read from. Defaults to None.
          use_environment_injection (bool, optional): Whether to use
          environment injection. Defaults to True.
        """

        # Store the file path and base key for YAML reading
        self._yaml_base_key: str | None = yaml_base_key
        self._file_path: Path = file_path

        # Store whether to use environment injection
        self._use_environment_injection: bool = use_environment_injection

    def _filter_data_with_base_key(self, yaml_data: dict) -> dict:
        """
        Extracts the data from the YAML file with the base key.
        Args:
            yaml_data (dict): The data from the YAML file.
        Returns:
            dict: The filtered data from the YAML file.
        Raises:
            KeyError: If the base key is not found in the YAML file.
        """
        if self._yaml_base_key is not None:
            _keys: list[str] = self._yaml_base_key.split(".")
            while len(_keys) != 0:
                try:
                    # /!\ pop don't accept index as keyword argument
                    _key = _keys.pop(0)
                    yaml_data = yaml_data[_key]
                except KeyError as _e:
                    raise KeyError(
                        f"Base key {_key} not found in YAML file"
                        + " from {self._yaml_base_key}"
                    ) from _e
        return yaml_data

    def _read_yaml_file(self, file_path: Path) -> dict:
        """
        Reads the YAML file and returns the data as a dictionary.
        Args:
            file_path (Path): The path to the YAML file.

        Returns:
            dict: The data from the YAML file.

        Raises:
            ValueError: If there is an error reading the file.
            FileNotFoundError: If the file is not found.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="UTF-8") as file:
            _loader = SafeLoader(file)

            try:
                _yaml_data = _loader.get_data()
            except Exception as _e:
                raise ValueError(f"Error reading YAML file: {file_path}") from _e

            return _yaml_data

    def _inject_environment_variables(
        self, yaml_data: dict | str | list
    ) -> dict | str | list:
        """
        Injects environment variables into the YAML data recursively.
        Args:
            yaml_data (dict | str | list): The data from the YAML file.
        Returns:
            dict: The data from the YAML file with environment variables injected.
        """
        if isinstance(yaml_data, dict):
            for _key, _value in yaml_data.items():
                yaml_data[_key] = self._inject_environment_variables(_value)
        elif isinstance(yaml_data, list):
            yaml_data = [
                self._inject_environment_variables(_value) for _value in yaml_data
            ]
        elif isinstance(yaml_data, str):
            while True:
                _match = self.re.search(yaml_data)
                if _match is None:
                    break
                _env_key = _match.group(1)
                _env_default = _match.group(2)
                _env_value = os.getenv(_env_key, _env_default)
                yaml_data = yaml_data.replace(_match.group(0), _env_value)

        return yaml_data

    def read(self) -> dict | str | list:
        """
        Reads the YAML file and converts it to a Pydantic model
        with or without environment injection.

        Raises:
            UnableToReadYamlFileError: If there is an error reading the file.
        """

        # Read the YAML file and filter the data with the base key
        try:
            _yaml_data: dict = self._filter_data_with_base_key(
                self._read_yaml_file(file_path=self._file_path)
            )
        except (FileNotFoundError, ValueError, KeyError) as _e:
            raise UnableToReadYamlFileError(
                file_path=self._file_path, message=str(_e)
            ) from _e

        if self._use_environment_injection:
            _yaml_data_with_env_injected: dict | str | list = (
                self._inject_environment_variables(_yaml_data)
            )
            return _yaml_data_with_env_injected
        else:
            return _yaml_data
