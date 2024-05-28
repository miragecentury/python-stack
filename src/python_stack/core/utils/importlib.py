""" Provide importlib functions """

from importlib.abc import Traversable
from importlib.resources import files


def get_path_file_in_package(filename: str, package: str) -> Traversable:
    """
    Return Absolute Path of file in package

    Args:
        filename (str): Filename to search
        package (str): Package name

    Returns:
        Traversable: File

    Raises:
        FileNotFoundError: If file not found
        ImportError: If package not found

    """
    try:
        path: Traversable = files(package).joinpath(filename)
    except FileNotFoundError as exception:
        raise FileNotFoundError(
            f"File {filename} not found in package {package}"
        ) from exception
    except ImportError as exception:
        raise ImportError(f"Package {package} not found") from exception
    return path
