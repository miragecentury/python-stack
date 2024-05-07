""" Provide importlib functions """

from importlib.resources import files
from os import PathLike


def get_path_file_in_package(filename: str, package: str) -> PathLike:
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
        _path = files(package).joinpath(filename)
    except FileNotFoundError as _e:
        raise FileNotFoundError(
            f"File {filename} not found in package {package}"
        ) from _e
    except ImportError as _e:
        raise ImportError(f"Package {package} not found") from _e
    return _path
