"""
Provides a helper class to inject environment variables in strings.
"""

import re


class EnvironmentInjectorHelper:
    """
    Facilitates injecting environment variables in strings.
    Expected to be use with YAMLFileReader.

    Detected patterns:
    - ${ENV_VAR}
    - ${ENV_VAR:default_value}
    - ${ENV_VAR:value${ENV_VAR2}}
    - ${ENV_VAR:value${ENV_VAR2:default_value2}}

    """

    class DetectedEnvironmentVariable:
        """
        Internal class to store detected environment variables.
        """

        pass

    PATTERN = re.compile(r".*(\${(\w+):?([\w\-\:\/\.]+)?}).*")

    def __init__(self, value: str) -> None:
        pass

    def detect(self) -> bool:
        """
        Detects whether the string contains an environment variable to inject.
        """
        pass

    def inject(self) -> str:
        pass
