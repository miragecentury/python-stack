"""
Provides a class for reading YAML files and converting them to Pydantic models.
"""

from typing import Generic, TypeVar, get_args

from pydantic import BaseModel
from yaml import SafeLoader, load

GenericPydanticModel = TypeVar("GenericPydanticModel", bound=BaseModel)


class YamlFileReader(Generic[GenericPydanticModel]):
    """
    Handles reading YAML files and converting them to Pydantic models.
    """

    def __init__(
        self,
        file_path: str,
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

        # Extract the generic class from the class definition.
        # https://peps.python.org/pep-0560/
        # pylint: disable=no-member
        self._generic_class: type = get_args(self.__orig_bases__[0])[0]

        # Store the file path and base key for YAML reading
        self._yaml_base_key: str | None = yaml_base_key
        self._file_path: str = file_path

        # Store whether to use environment injection
        self._use_environment_injection: bool = use_environment_injection

    def read(self, file_path: str) -> GenericPydanticModel:
        """
        Reads the YAML file and converts it to a Pydantic model
        with or without environment injection.
        """
        with open(file_path, "r") as file:
            yaml_data = load(file, Loader=SafeLoader)
