"""
Provides exceptions for the http_client_plugin module.
"""


class HttpClientPluginBaseException(Exception):
    """
    Provides a base exception for the http_client_plugin module.
    """


class UnableToBuildConfigError(HttpClientPluginBaseException):
    """
    Raised when there is an error building the configuration
    for the http client plugin.
    """
